from datetime import date, timedelta

from app.dependencies import get_current_user, get_db, require_admin
from app.models.objectif import Objectif
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurResponse,
    UtilisateurUpdate,
)
from app.security import hash_password
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])

GOAL_DEFINITIONS = {
    "destresse": {
        "type_objectif": "Destresse",
        "description": "Reduire mon stress",
    },
    "sante": {
        "type_objectif": "Sante",
        "description": "Ameliorer ma sante generale",
    },
    "perte_de_poids": {
        "type_objectif": "Perte de poids",
        "description": "Perdre du poids",
    },
    "performance": {
        "type_objectif": "Performance",
        "description": "Ameliorer mes performances sportives",
    },
    "endurance": {
        "type_objectif": "Endurance",
        "description": "Gagner en endurance",
    },
    "force": {
        "type_objectif": "Force",
        "description": "Developper ma force musculaire",
    },
}


def _sync_user_goal_rows(utilisateur: Utilisateur, db: Session) -> None:
    date_debut = utilisateur.date_inscription or date.today()
    date_fin = date_debut + timedelta(days=90)

    for flag_name, goal in GOAL_DEFINITIONS.items():
        existing_goal = (
            db.query(Objectif)
            .filter(
                Objectif.id_utilisateur == utilisateur.id_utilisateur,
                Objectif.type_objectif == goal["type_objectif"],
                Objectif.description == goal["description"],
            )
            .first()
        )

        if getattr(utilisateur, flag_name, False):
            if existing_goal is None:
                db.add(
                    Objectif(
                        type_objectif=goal["type_objectif"],
                        description=goal["description"],
                        date_debut=date_debut,
                        date_fin=date_fin,
                        statut="en_cours",
                        id_utilisateur=utilisateur.id_utilisateur,
                    )
                )
        elif existing_goal is not None:
            db.delete(existing_goal)


def _create_user(utilisateur: UtilisateurCreate, db: Session, *, is_admin: bool = False) -> Utilisateur:
    existing_user = db.query(Utilisateur).filter(Utilisateur.username == utilisateur.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est deja utilise")

    existing_email = db.query(Utilisateur).filter(Utilisateur.email == utilisateur.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Cette adresse mail est deja utilisee")

    data = utilisateur.model_dump(exclude={"password"})
    data["password_hash"] = hash_password(utilisateur.password)
    data["is_admin"] = is_admin

    new_user = Utilisateur(**data)
    db.add(new_user)
    db.flush()
    _sync_user_goal_rows(new_user, db)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/register", response_model=UtilisateurResponse, status_code=201)
def register(utilisateur: UtilisateurCreate, db: Session = Depends(get_db)):
    """Public registration endpoint used by the frontend inscription page."""
    return _create_user(utilisateur, db, is_admin=False)


@router.post("/", response_model=UtilisateurResponse, status_code=201)
def create_utilisateur(
    utilisateur: UtilisateurCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    """Admin-only user creation endpoint."""
    return _create_user(utilisateur, db, is_admin=False)


@router.get("/", response_model=list[UtilisateurResponse])
def get_utilisateurs(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(Utilisateur).all()


@router.get("/{utilisateur_id}", response_model=UtilisateurResponse)
def get_utilisateur_by_id(
    utilisateur_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == utilisateur_id).first()
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")

    return utilisateur


@router.put("/{utilisateur_id}", response_model=UtilisateurResponse)
def update_utilisateur(
    utilisateur_id: int,
    utilisateur_update: UtilisateurUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not user.get("is_admin", False) and str(utilisateur_id) != str(user.get("sub")):
        raise HTTPException(status_code=403, detail="Admin only")

    utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == utilisateur_id).first()
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")

    for key, value in utilisateur_update.model_dump(exclude_none=True).items():
        setattr(utilisateur, key, value)

    _sync_user_goal_rows(utilisateur, db)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


@router.delete("/{utilisateur_id}", status_code=204)
def delete_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == utilisateur_id).first()
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")

    db.delete(utilisateur)
    db.commit()
