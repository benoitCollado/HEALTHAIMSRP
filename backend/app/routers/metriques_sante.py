from app.dependencies import get_current_user, get_db, require_admin
from app.models.metrique_sante import MetriqueSante
from app.schemas.metrique_sante import (
    MetriqueSanteCreate,
    MetriqueSanteResponse,
    MetriqueSanteUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

# Routeur pour les endpoints liés aux métriques de santé
router = APIRouter(prefix="/metriques-sante", tags=["MetriquesSante"])

# Schéma OAuth2 pour récupérer le token JWT depuis /login

# Dépendance pour ouvrir et fermer une session de base de données

# Récupère l’utilisateur courant à partir du token JWT

# Vérifie que l’utilisateur est administrateur


# Création d’une nouvelle métrique de santé
@router.post("/", response_model=MetriqueSanteResponse, status_code=201)
def create_metrique_sante(
    metrique: MetriqueSanteCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    new_metrique = MetriqueSante(**metrique.model_dump())
    db.add(new_metrique)
    db.commit()
    db.refresh(new_metrique)
    return new_metrique


# Récupération de toutes les métriques de santé
@router.get("/", response_model=list[MetriqueSanteResponse])
def get_metriques_sante(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(MetriqueSante).all()


# Récupération d’une métrique de santé par identifiant
@router.get("/{metrique_id}", response_model=MetriqueSanteResponse)
def get_metrique_sante_by_id(
    metrique_id: int = Path(..., gt=0), db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    metrique = db.query(MetriqueSante).filter(MetriqueSante.id_metrique == metrique_id).first()

    if metrique is None:
        raise HTTPException(status_code=404, detail="Metrique non trouvée")

    return metrique


# Mise à jour d’une métrique de santé existante
@router.put("/{metrique_id}", response_model=MetriqueSanteResponse)
def update_metrique_sante(
    metrique_id: int,
    metrique_update: MetriqueSanteUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    metrique = db.query(MetriqueSante).filter(MetriqueSante.id_metrique == metrique_id).first()

    if metrique is None:
        raise HTTPException(status_code=404, detail="Metrique non trouvée")

    for key, value in metrique_update.model_dump(exclude_none=True).items():
        setattr(metrique, key, value)

    db.commit()
    db.refresh(metrique)
    return metrique


# Suppression d’une métrique de santé (réservée aux administrateurs)
@router.delete("/{metrique_id}", status_code=204)
def delete_metrique_sante(metrique_id: int, db: Session = Depends(get_db), user: dict = Depends(require_admin)):
    metrique = db.query(MetriqueSante).filter(MetriqueSante.id_metrique == metrique_id).first()

    if metrique is None:
        raise HTTPException(status_code=404, detail="Metrique non trouvée")

    db.delete(metrique)
    db.commit()
