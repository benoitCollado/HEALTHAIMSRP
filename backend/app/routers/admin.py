"""
Routeur admin : tableau de bord, flux de données (Airflow), anomalies, export.
Réservé aux utilisateurs avec is_admin=True.
"""
import os
from datetime import date, timedelta
from io import StringIO
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.activite import Activite
from app.models.consommation import Consommation
from app.models.metrique_sante import MetriqueSante
from app.models.objectif import Objectif
from app.models.utilisateur import Utilisateur
from app.security import verify_token

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def require_admin(user: dict = Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin only")
    return user


class CorrectionBody(BaseModel):
    statut: Optional[str] = None
    quantite_g: Optional[float] = None
    calories_calculees: Optional[float] = None
    poids_kg: Optional[float] = None
    frequence_cardiaque: Optional[int] = None
    duree_sommeil_h: Optional[float] = None


def _normalize_statut(s: Optional[str]) -> str:
    if not s:
        return "refuse"
    s = s.lower()
    if "term" in s or "valid" in s:
        return "valide"
    if "cours" in s or "actif" in s:
        return "encours"
    if "refus" in s or "rejet" in s:
        return "refuse"
    return "encours"


def _float_or_none(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ============ Dashboard KPIs ============


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """
    KPIs pour le tableau de bord admin :
    - Qualité des données
    - Progression utilisateurs
    - Tendances nutrition et activité
    - KPIs business
    """
    today = date.today()
    last_30 = today - timedelta(days=30)
    last_7 = today - timedelta(days=7)

    # Objectifs par statut
    objectifs = db.query(Objectif).all()
    valides = sum(1 for o in objectifs if _normalize_statut(o.statut) == "valide")
    encours = sum(1 for o in objectifs if _normalize_statut(o.statut) == "encours")
    refuses = sum(1 for o in objectifs if _normalize_statut(o.statut) == "refuse")
    total_obj = len(objectifs)
    taux_validation = round((valides / total_obj * 100) if total_obj else 0, 1)

    # Utilisateurs
    nb_utilisateurs = db.query(Utilisateur).count()
    nouveaux_7j = db.query(Utilisateur).filter(
        Utilisateur.date_inscription >= last_7
    ).count()
    nouveaux_30j = db.query(Utilisateur).filter(
        Utilisateur.date_inscription >= last_30
    ).count()

    # Consommations (nutrition)
    nb_consommations = db.query(Consommation).count()
    consommations_7j = db.query(Consommation).filter(
        Consommation.date_consommation >= last_7
    ).count()
    calories_moy = db.query(func.avg(Consommation.calories_calculees)).scalar()
    calories_moy = _float_or_none(calories_moy) or 0

    # Activités
    nb_activites = db.query(Activite).count()
    activites_7j = db.query(Activite).filter(
        Activite.date_activite >= last_7
    ).count()
    duree_totale = db.query(func.sum(Activite.duree_minutes)).scalar()
    duree_totale = int(_float_or_none(duree_totale) or 0)

    # Métriques
    nb_metriques = db.query(MetriqueSante).count()

    # Anomalies (estimation)
    anomalies_obj = refuses
    consommations_invalides = db.query(Consommation).filter(
        (Consommation.quantite_g <= 0) | (Consommation.calories_calculees < 0)
    ).count()
    metriques_aberrantes = db.query(MetriqueSante).filter(
        (MetriqueSante.poids_kg < 0) | (MetriqueSante.poids_kg > 300) |
        (MetriqueSante.frequence_cardiaque < 0) | (MetriqueSante.frequence_cardiaque > 250) |
        (MetriqueSante.duree_sommeil_h < 0) | (MetriqueSante.duree_sommeil_h > 24)
    ).count()
    total_anomalies = anomalies_obj + consommations_invalides + metriques_aberrantes

    total_donnees = nb_consommations + nb_activites + nb_metriques
    qualite_pct = round(
        ((total_donnees - consommations_invalides - metriques_aberrantes) / total_donnees * 100)
        if total_donnees else 100, 1
    )

    return {
        "qualite_donnees": {
            "score_pct": qualite_pct,
            "total_anomalies": total_anomalies,
            "objectifs_refuses": anomalies_obj,
            "consommations_invalides": consommations_invalides,
            "metriques_aberrantes": metriques_aberrantes,
        },
        "progression_utilisateurs": {
            "total": nb_utilisateurs,
            "nouveaux_7j": nouveaux_7j,
            "nouveaux_30j": nouveaux_30j,
        },
        "tendances_nutrition": {
            "total_consommations": nb_consommations,
            "consommations_7j": consommations_7j,
            "calories_moyennes": round(calories_moy, 1),
        },
        "tendances_activite": {
            "total_activites": nb_activites,
            "activites_7j": activites_7j,
            "duree_totale_minutes": duree_totale,
        },
        "objectifs": {
            "valides": valides,
            "encours": encours,
            "refuses": refuses,
            "taux_validation_pct": taux_validation,
        },
        "kpis_business": {
            "utilisateurs_actifs_30j": nouveaux_30j + nb_utilisateurs,  # approximation
            "donnees_sante_total": nb_consommations + nb_activites + nb_metriques,
        },
    }


# ============ Flux de données (Airflow ETL) ============

# Descriptions des DAGs pour l'affichage
DAG_DESCRIPTIONS = {
    "fetch_openfoodfacts_france": "Import Open Food Facts → CSV intermédiaire (validation admin requise)",
    "export_db_to_csv": "Export BDD → CSV intermédiaire (validation admin requise)",
    "incorporation_ml": "Incorpore les CSV validés : import→BDD, export→dossier ML (toutes les heures)",
}


# DAGs HealthAim à afficher (flux ETL administrables)
HEALTHAIM_DAG_IDS = ["fetch_openfoodfacts_france", "export_db_to_csv", "incorporation_ml"]


def _fetch_airflow_dag_runs() -> dict:
    """
    Récupère les DAGs et leurs runs depuis l'API REST Airflow.
    Retourne {dag_id: {runs: [...], last_run: {...}}} ou {} si Airflow indisponible.
    """
    base_url = os.getenv("AIRFLOW_API_URL", "http://airflow-webserver:8080").rstrip("/")
    user = os.getenv("AIRFLOW_USER", "airflow")
    password = os.getenv("AIRFLOW_PASSWORD", "airflow")
    auth = (user, password) if user and password else None

    result = {}
    try:
        with httpx.Client(timeout=10.0) as client:
            # Liste des DAGs (on ne garde que les DAGs HealthAim)
            r = client.get(f"{base_url}/api/v1/dags", auth=auth)
            if r.status_code != 200:
                return result
            dags_data = r.json()
            all_dag_ids = [d["dag_id"] for d in dags_data.get("dags", [])]
            dag_ids = [did for did in HEALTHAIM_DAG_IDS if did in all_dag_ids]
            if not dag_ids:
                dag_ids = HEALTHAIM_DAG_IDS  # on affiche quand même, avec runs vides

            for dag_id in dag_ids:
                # Derniers runs du DAG
                r2 = client.get(
                    f"{base_url}/api/v1/dags/{dag_id}/dagRuns",
                    params={"limit": 10},
                    auth=auth,
                )
                if r2.status_code != 200:
                    result[dag_id] = {"runs": [], "last_run": None}
                    continue
                runs_data = r2.json()
                runs = runs_data.get("dag_runs", [])
                last_run = runs[0] if runs else None
                result[dag_id] = {"runs": runs, "last_run": last_run}
    except (httpx.ConnectError, httpx.TimeoutException, Exception):
        pass
    return result


def _build_flux_from_airflow(airflow_data: dict, db: Session) -> dict:
    """Construit la structure flux (valides, encours, refuses) à partir des runs Airflow."""
    valides = []
    encours = []
    refuses = []

    for dag_id in HEALTHAIM_DAG_IDS:
        data = airflow_data.get(dag_id, {"runs": [], "last_run": None})
        runs = data.get("runs", [])
        last_run = data.get("last_run")
        desc = DAG_DESCRIPTIONS.get(dag_id, f"DAG {dag_id}")

        run_id = last_run.get("run_id", "-") if last_run else "-"
        state = (last_run or {}).get("state", "unknown")
        start_date = (last_run or {}).get("start_date")
        last_run_str = str(start_date)[:10] if start_date else "-"

        item = {
            "id": dag_id,
            "type": "dag",
            "nom": dag_id.replace("_", " ").title(),
            "description": desc,
            "statut": state,
            "dag_id": dag_id,
            "run_id": run_id,
            "stats": {"lastRun": last_run_str},
        }

        if state in ("running", "queued"):
            encours.append(item)
        elif state == "success":
            valides.append(item)
        else:
            item["errors"] = [f"Échec du run : {state}"] if state not in ("unknown",) else ["Aucune exécution récente"]
            refuses.append(item)

    # Métadonnées des données en base (complément)
    nb_cons = db.query(Consommation).count()
    nb_act = db.query(Activite).count()
    nb_met = db.query(MetriqueSante).count()
    derniere_cons = db.query(func.max(Consommation.date_consommation)).scalar()
    derniere_act = db.query(func.max(Activite.date_activite)).scalar()
    derniere_met = db.query(func.max(MetriqueSante.date_mesure)).scalar()

    return {
        "valides": valides,
        "encours": encours,
        "refuses": refuses,
        "flux_metadonnees": {
            "consommations": {"total": nb_cons, "dernier_run": str(derniere_cons) if derniere_cons else None},
            "activites": {"total": nb_act, "dernier_run": str(derniere_act) if derniere_act else None},
            "metriques": {"total": nb_met, "dernier_run": str(derniere_met) if derniere_met else None},
        },
        "airflow_disponible": bool(airflow_data),
    }


@router.get("/flux")
def get_flux(
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """
    Liste des flux de données ETL (DAGs Airflow) : fetch_openfoodfacts_france, export_db_to_csv.
    Retourne les runs par statut : en cours, réussis, en échec.
    """
    airflow_data = _fetch_airflow_dag_runs()
    return _build_flux_from_airflow(airflow_data, db)


# ============ CSV intermédiaires (visualisation, modification, validation) ============

import json as _json
from pathlib import Path as _Path

DATA_DIR = _Path(os.getenv("DATA_DIR", "/data"))
INTERMEDIATE_IMPORT = DATA_DIR / "intermediate" / "import"
INTERMEDIATE_EXPORT = DATA_DIR / "intermediate" / "export"


def _safe_filename(name: str) -> bool:
    """Vérifie que le nom de fichier est sûr (pas de path traversal)."""
    if not name or ".." in name or "/" in name or "\\" in name:
        return False
    return name.endswith(".csv") and (name.startswith("import_") or name.startswith("export_"))


def _get_csv_path(filename: str) -> _Path:
    if not _safe_filename(filename):
        raise HTTPException(status_code=400, detail="Nom de fichier invalide")
    if filename.startswith("import_"):
        path = INTERMEDIATE_IMPORT / filename
    else:
        path = INTERMEDIATE_EXPORT / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    return path


def _get_meta_path(filename: str) -> _Path:
    base = filename.replace(".csv", "")
    meta_name = base + ".json"
    if filename.startswith("import_"):
        return INTERMEDIATE_IMPORT / meta_name
    return INTERMEDIATE_EXPORT / meta_name


@router.get("/flux/csv")
def list_flux_csv(
    type_csv: Optional[str] = Query(None, description="import | export"),
    status: Optional[str] = Query(None, description="pending | validated | rejected | incorporated"),
    user: dict = Depends(require_admin),
):
    """
    Liste les CSV intermédiaires (import et/ou export) avec métadonnées.
    """
    result = {"import": [], "export": []}
    for csv_type, base_dir in [("import", INTERMEDIATE_IMPORT), ("export", INTERMEDIATE_EXPORT)]:
        if type_csv and type_csv != csv_type:
            continue
        if not base_dir.exists():
            continue
        prefix = "import_" if csv_type == "import" else "export_"
        for meta_path in sorted(base_dir.glob(f"{prefix}*.json"), reverse=True):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = _json.load(f)
                if status and meta.get("status") != status:
                    continue
                meta["csv_type"] = csv_type
                result[csv_type].append(meta)
            except Exception:
                pass
    return result


@router.get("/flux/csv/{filename}")
def get_flux_csv_content(
    filename: str,
    user: dict = Depends(require_admin),
):
    """Retourne le contenu d'un CSV intermédiaire (pour visualisation)."""
    path = _get_csv_path(filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    meta_path = _get_meta_path(filename)
    meta = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = _json.load(f)
    return {"content": content, "metadata": meta}


class CsvUpdateBody(BaseModel):
    content: str


@router.put("/flux/csv/{filename}")
def update_flux_csv(
    filename: str,
    body: CsvUpdateBody = Body(...),
    user: dict = Depends(require_admin),
):
    """Met à jour le contenu d'un CSV intermédiaire (modification avant validation)."""
    path = _get_csv_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body.content)
    meta_path = _get_meta_path(filename)
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = _json.load(f)
        lines = [l for l in body.content.strip().split("\n") if l.strip()]
        meta["rows"] = max(0, len(lines) - 1) if lines and (lines[0].startswith("type,") or lines[0].startswith("nom_aliment,")) else len(lines)
        with open(meta_path, "w", encoding="utf-8") as f:
            _json.dump(meta, f, indent=2)
    return {"success": True, "message": "CSV mis à jour"}


@router.post("/flux/csv/{filename}/validate")
def validate_flux_csv(
    filename: str,
    user: dict = Depends(require_admin),
):
    """Valide un CSV intermédiaire. incorporation_ml le chargera à la prochaine exécution."""
    _get_csv_path(filename)
    meta_path = _get_meta_path(filename)
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Métadonnées non trouvées")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = _json.load(f)
    meta["status"] = "validated"
    with open(meta_path, "w", encoding="utf-8") as f:
        _json.dump(meta, f, indent=2)
    return {"success": True, "message": "CSV validé", "status": "validated"}


@router.post("/flux/csv/{filename}/reject")
def reject_flux_csv(
    filename: str,
    user: dict = Depends(require_admin),
):
    """Refuse un CSV intermédiaire."""
    _get_csv_path(filename)
    meta_path = _get_meta_path(filename)
    if not meta_path.exists():
        raise HTTPException(status_code=404, detail="Métadonnées non trouvées")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = _json.load(f)
    meta["status"] = "rejected"
    with open(meta_path, "w", encoding="utf-8") as f:
        _json.dump(meta, f, indent=2)
    return {"success": True, "message": "CSV refusé", "status": "rejected"}


# ============ Utilisateurs (recherche et données) ============


@router.get("/utilisateurs")
def search_utilisateurs(
    q: Optional[str] = Query(None, description="Recherche par nom d'utilisateur (substring)"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """
    Liste des utilisateurs avec recherche par username.
    Retourne pour chaque utilisateur : id, username, profil, statistiques (nb consommations, activités, métriques, objectifs).
    """
    query = db.query(Utilisateur)
    if q and q.strip():
        search = f"%{q.strip()}%"
        query = query.filter(Utilisateur.username.ilike(search))

    utilisateurs = query.order_by(Utilisateur.username).all()
    result = []

    for u in utilisateurs:
        nb_cons = db.query(Consommation).filter(Consommation.id_utilisateur == u.id_utilisateur).count()
        nb_act = db.query(Activite).filter(Activite.id_utilisateur == u.id_utilisateur).count()
        nb_met = db.query(MetriqueSante).filter(MetriqueSante.id_utilisateur == u.id_utilisateur).count()
        nb_obj = db.query(Objectif).filter(Objectif.id_utilisateur == u.id_utilisateur).count()

        result.append({
            "id_utilisateur": u.id_utilisateur,
            "username": u.username,
            "age": u.age,
            "sexe": u.sexe,
            "taille_cm": u.taille_cm,
            "poids_kg": u.poids_kg,
            "niveau_activite": u.niveau_activite,
            "type_abonnement": u.type_abonnement,
            "date_inscription": str(u.date_inscription),
            "is_admin": u.is_admin,
            "stats": {
                "nb_consommations": nb_cons,
                "nb_activites": nb_act,
                "nb_metriques": nb_met,
                "nb_objectifs": nb_obj,
            },
        })

    return {"utilisateurs": result, "total": len(result)}


@router.get("/utilisateurs/{utilisateur_id}")
def get_utilisateur_donnees(
    utilisateur_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """
    Détail d'un utilisateur avec toutes ses données : consommations, activités, métriques, objectifs.
    """
    u = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == utilisateur_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    consommations = db.query(Consommation).filter(Consommation.id_utilisateur == utilisateur_id).all()
    activites = db.query(Activite).filter(Activite.id_utilisateur == utilisateur_id).all()
    metriques = db.query(MetriqueSante).filter(MetriqueSante.id_utilisateur == utilisateur_id).all()
    objectifs = db.query(Objectif).filter(Objectif.id_utilisateur == utilisateur_id).all()

    def _serialize_cons(c):
        return {
            "id_consommation": c.id_consommation,
            "date_consommation": str(c.date_consommation),
            "quantite_g": float(c.quantite_g) if c.quantite_g else 0,
            "calories_calculees": float(c.calories_calculees) if c.calories_calculees else 0,
            "id_aliment": c.id_aliment,
        }

    def _serialize_act(a):
        return {
            "id_activite": a.id_activite,
            "date_activite": str(a.date_activite),
            "duree_minutes": a.duree_minutes,
            "calories_depensees": float(a.calories_depensees) if a.calories_depensees else 0,
            "id_exercice": a.id_exercice,
        }

    def _serialize_met(m):
        return {
            "id_metrique": m.id_metrique,
            "date_mesure": str(m.date_mesure),
            "poids_kg": float(m.poids_kg) if m.poids_kg is not None else None,
            "frequence_cardiaque": m.frequence_cardiaque,
            "duree_sommeil_h": float(m.duree_sommeil_h) if m.duree_sommeil_h is not None else None,
            "calories_brulees": m.calories_brulees,
            "pas": m.pas,
        }

    def _serialize_obj(o):
        return {
            "id_objectif": o.id_objectif,
            "type_objectif": o.type_objectif,
            "description": o.description,
            "date_debut": str(o.date_debut),
            "date_fin": str(o.date_fin),
            "statut": o.statut,
        }

    return {
        "utilisateur": {
            "id_utilisateur": u.id_utilisateur,
            "username": u.username,
            "age": u.age,
            "sexe": u.sexe,
            "taille_cm": u.taille_cm,
            "poids_kg": u.poids_kg,
            "niveau_activite": u.niveau_activite,
            "type_abonnement": u.type_abonnement,
            "date_inscription": str(u.date_inscription),
            "is_admin": u.is_admin,
        },
        "consommations": [_serialize_cons(c) for c in consommations],
        "activites": [_serialize_act(a) for a in activites],
        "metriques": [_serialize_met(m) for m in metriques],
        "objectifs": [_serialize_obj(o) for o in objectifs],
    }


# ============ Anomalies ============


@router.get("/anomalies")
def get_anomalies(
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
    type_anomalie: Optional[str] = Query(None, description="objectif_refuse | consommation_invalide | metrique_incoherente"),
):
    """
    Liste des anomalies détectées.
    """
    anomalies = []

    # Objectifs refusés
    if type_anomalie is None or type_anomalie == "objectif_refuse":
        for o in db.query(Objectif).filter(
            func.lower(Objectif.statut).like("%refus%")
        ).all():
            anomalies.append({
                "id": f"obj-{o.id_objectif}",
                "type": "objectif_refuse",
                "type_affichage": "Objectif refusé",
                "id_entite": o.id_objectif,
                "entite_type": "objectif",
                "description": f"Objectif {o.type_objectif} : {o.description}",
                "detail": o.statut,
            })

    # Consommations invalides
    if type_anomalie is None or type_anomalie == "consommation_invalide":
        for c in db.query(Consommation).filter(
            (Consommation.quantite_g <= 0) | (Consommation.calories_calculees < 0)
        ).all():
            anomalies.append({
                "id": f"cons-{c.id_consommation}",
                "type": "consommation_invalide",
                "type_affichage": "Consommation invalide",
                "id_entite": c.id_consommation,
                "entite_type": "consommation",
                "description": f"Consommation #{c.id_consommation} : quantite={c.quantite_g}, calories={c.calories_calculees}",
                "detail": "Quantité ou calories négatives/nulles",
            })

    # Métriques aberrantes
    if type_anomalie is None or type_anomalie == "metrique_incoherente":
        for m in db.query(MetriqueSante).filter(
            (MetriqueSante.poids_kg < 0) | (MetriqueSante.poids_kg > 300) |
            (MetriqueSante.frequence_cardiaque < 0) | (MetriqueSante.frequence_cardiaque > 250) |
            (MetriqueSante.duree_sommeil_h < 0) | (MetriqueSante.duree_sommeil_h > 24)
        ).all():
            anomalies.append({
                "id": f"met-{m.id_metrique}",
                "type": "metrique_incoherente",
                "type_affichage": "Métrique incohérente",
                "id_entite": m.id_metrique,
                "entite_type": "metrique",
                "description": f"Métrique #{m.id_metrique} : poids={m.poids_kg}, FC={m.frequence_cardiaque}, sommeil={m.duree_sommeil_h}",
                "detail": "Valeurs hors plages réalistes",
            })

    return {"anomalies": anomalies, "total": len(anomalies)}


@router.post("/anomalies/{anomalie_id}/valider")
def valider_anomalie(
    anomalie_id: str = Path(...),
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """
    Valider une anomalie (marquer comme traitée).
    Pour objectif_refuse : passer le statut à "Terminé".
    Pour consommation_invalide / metrique_incoherente : on considère que "valider" = ignorer (pas de modification).
    """
    if anomalie_id.startswith("obj-"):
        oid = int(anomalie_id.replace("obj-", ""))
        obj = db.query(Objectif).filter(Objectif.id_objectif == oid).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Objectif non trouvé")
        obj.statut = "Terminé"
        db.commit()
        return {"success": True, "message": "Objectif marqué comme terminé"}
    # Pour cons et met : on ne modifie pas, on considère "validé" = accepté tel quel
    return {"success": True, "message": "Anomalie validée (aucune modification)"}


@router.post("/anomalies/{anomalie_id}/corriger")
def corriger_anomalie(
    anomalie_id: str = Path(...),
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
    correction: Optional[CorrectionBody] = Body(default=None),
):
    """
    Corriger une anomalie.
    - objectif : correction.statut
    - consommation : correction.quantite_g, correction.calories_calculees
    - metrique : correction.poids_kg, correction.frequence_cardiaque, correction.duree_sommeil_h
    """
    corr = (correction.model_dump(exclude_none=True) if correction else {}) or {}

    if anomalie_id.startswith("obj-"):
        oid = int(anomalie_id.replace("obj-", ""))
        obj = db.query(Objectif).filter(Objectif.id_objectif == oid).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Objectif non trouvé")
        if "statut" in corr:
            obj.statut = corr["statut"]
        else:
            obj.statut = "Terminé"
        db.commit()
        return {"success": True, "message": "Objectif corrigé"}

    if anomalie_id.startswith("cons-"):
        cid = int(anomalie_id.replace("cons-", ""))
        c = db.query(Consommation).filter(Consommation.id_consommation == cid).first()
        if not c:
            raise HTTPException(status_code=404, detail="Consommation non trouvée")
        if "quantite_g" in corr:
            c.quantite_g = corr["quantite_g"]
        if "calories_calculees" in corr:
            c.calories_calculees = corr["calories_calculees"]
        if float(c.quantite_g or 0) <= 0:
            c.quantite_g = 1.0
        if float(c.calories_calculees or 0) < 0:
            c.calories_calculees = 0.0
        db.commit()
        return {"success": True, "message": "Consommation corrigée"}

    if anomalie_id.startswith("met-"):
        mid = int(anomalie_id.replace("met-", ""))
        m = db.query(MetriqueSante).filter(MetriqueSante.id_metrique == mid).first()
        if not m:
            raise HTTPException(status_code=404, detail="Métrique non trouvée")
        if "poids_kg" in corr:
            m.poids_kg = corr["poids_kg"]
        if "frequence_cardiaque" in corr:
            m.frequence_cardiaque = corr["frequence_cardiaque"]
        if "duree_sommeil_h" in corr:
            m.duree_sommeil_h = corr["duree_sommeil_h"]
        # Clamp valeurs aberrantes
        if m.poids_kg is not None and (float(m.poids_kg) < 0 or float(m.poids_kg) > 300):
            m.poids_kg = 70.0
        if m.frequence_cardiaque is not None and (m.frequence_cardiaque < 0 or m.frequence_cardiaque > 250):
            m.frequence_cardiaque = 72
        if m.duree_sommeil_h is not None and (float(m.duree_sommeil_h) < 0 or float(m.duree_sommeil_h) > 24):
            m.duree_sommeil_h = 7.0
        db.commit()
        return {"success": True, "message": "Métrique corrigée"}

    raise HTTPException(status_code=400, detail="Format d'anomalie inconnu")


# ============ Export ============


@router.get("/export")
def export_donnees_nettoyees(
    format_type: str = Query("csv", description="csv"),
    type_donnees: Optional[str] = Query(None, description="consommations | activites | metriques | objectifs | all"),
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """
    Export des données nettoyées (sans anomalies) en CSV.
    """
    if format_type != "csv":
        raise HTTPException(status_code=400, detail="Seul le format CSV est supporté")

    types = ["consommations", "activites", "metriques", "objectifs"] if type_donnees == "all" or not type_donnees else [type_donnees]
    buffer = StringIO()
    first = True

    for t in types:
        if t == "consommations":
            rows = db.query(Consommation).filter(
                Consommation.quantite_g > 0,
                Consommation.calories_calculees >= 0
            ).all()
            if not rows:
                continue
            if not first:
                buffer.write("\n")
            buffer.write("id_consommation,date_consommation,quantite_g,calories_calculees,id_aliment,id_utilisateur\n")
            for r in rows:
                buffer.write(f"{r.id_consommation},{r.date_consommation},{r.quantite_g},{r.calories_calculees},{r.id_aliment},{r.id_utilisateur}\n")
            first = False

        elif t == "activites":
            rows = db.query(Activite).all()
            if not rows:
                continue
            if not first:
                buffer.write("\n")
            buffer.write("id_activite,date_activite,duree_minutes,calories_depensees,id_exercice,id_utilisateur\n")
            for r in rows:
                buffer.write(f"{r.id_activite},{r.date_activite},{r.duree_minutes},{r.calories_depensees},{r.id_exercice},{r.id_utilisateur}\n")
            first = False

        elif t == "metriques":
            rows = db.query(MetriqueSante).filter(
                (MetriqueSante.poids_kg.is_(None)) | ((MetriqueSante.poids_kg >= 0) & (MetriqueSante.poids_kg <= 300)),
                (MetriqueSante.frequence_cardiaque.is_(None)) | ((MetriqueSante.frequence_cardiaque >= 0) & (MetriqueSante.frequence_cardiaque <= 250)),
                (MetriqueSante.duree_sommeil_h.is_(None)) | ((MetriqueSante.duree_sommeil_h >= 0) & (MetriqueSante.duree_sommeil_h <= 24))
            ).all()
            if not rows:
                continue
            if not first:
                buffer.write("\n")
            buffer.write("id_metrique,date_mesure,poids_kg,frequence_cardiaque,duree_sommeil_h,calories_brulees,pas,id_utilisateur\n")
            for r in rows:
                buffer.write(f"{r.id_metrique},{r.date_mesure},{r.poids_kg or ''},{r.frequence_cardiaque or ''},{r.duree_sommeil_h or ''},{r.calories_brulees or ''},{r.pas or ''},{r.id_utilisateur}\n")
            first = False

        elif t == "objectifs":
            rows = db.query(Objectif).filter(
                ~func.lower(Objectif.statut).like("%refus%")
            ).all()
            if not rows:
                continue
            if not first:
                buffer.write("\n")
            buffer.write("id_objectif,type_objectif,description,date_debut,date_fin,statut,id_utilisateur\n")
            for r in rows:
                buffer.write(f"{r.id_objectif},{r.type_objectif},{r.description},{r.date_debut},{r.date_fin},{r.statut},{r.id_utilisateur}\n")
            first = False

    content = buffer.getvalue()
    if not content.strip():
        raise HTTPException(status_code=404, detail="Aucune donnée à exporter")

    filename = f"donnees_nettoyees_{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
