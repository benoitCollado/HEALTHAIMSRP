from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_admin
from app.models.objectif import Objectif
from app.schemas.objectif import (
    ObjectifCreate,
    ObjectifResponse,
    ObjectifUpdate,
)

# Routeur pour les endpoints liés aux objectifs
router = APIRouter(
    prefix="/objectifs",
    tags=["Objectifs"]
)

# Schéma OAuth2 pour récupérer le token JWT depuis /login

# Dépendance pour ouvrir et fermer une session de base de données

# Récupère l’utilisateur courant à partir du token JWT

# Vérifie que l’utilisateur est administrateur

# Création d’un nouvel objectif
@router.post("/", response_model=ObjectifResponse, status_code=201)
def create_objectif(
    objectif: ObjectifCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    new_objectif = Objectif(**objectif.model_dump())
    db.add(new_objectif)
    db.commit()
    db.refresh(new_objectif)
    return new_objectif

# Récupération de tous les objectifs
@router.get("/", response_model=list[ObjectifResponse])
def get_objectifs(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Objectif).all()

# Récupération d’un objectif par identifiant
@router.get("/{objectif_id}", response_model=ObjectifResponse)
def get_objectif_by_id(
    objectif_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    objectif = db.query(Objectif).filter(
        Objectif.id_objectif == objectif_id
    ).first()

    if objectif is None:
        raise HTTPException(status_code=404, detail="Objectif non trouvé")

    return objectif

# Mise à jour d’un objectif existant
@router.put("/{objectif_id}", response_model=ObjectifResponse)
def update_objectif(
    objectif_id: int,
    objectif_update: ObjectifUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    objectif = db.query(Objectif).filter(
        Objectif.id_objectif == objectif_id
    ).first()

    if objectif is None:
        raise HTTPException(status_code=404, detail="Objectif non trouvé")

    for key, value in objectif_update.model_dump(exclude_none=True).items():
        setattr(objectif, key, value)

    db.commit()
    db.refresh(objectif)
    return objectif

# Suppression d’un objectif (réservée aux administrateurs)
@router.delete("/{objectif_id}", status_code=204)
def delete_objectif(
    objectif_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    objectif = db.query(Objectif).filter(
        Objectif.id_objectif == objectif_id
    ).first()

    if objectif is None:
        raise HTTPException(status_code=404, detail="Objectif non trouvé")

    db.delete(objectif)
    db.commit()
