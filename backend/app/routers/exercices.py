from app.dependencies import get_current_user, get_db, require_admin
from app.models.exercice import Exercice
from app.schemas.exercice import (
    ExerciceCreate,
    ExerciceResponse,
    ExerciceUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

# Routeur principal pour les endpoints liés aux exercices
router = APIRouter(prefix="/exercices", tags=["Exercices"])

# Schéma OAuth2 pour extraire le token JWT depuis /login

# Dépendance pour créer et fermer une session de base de données

# Récupère l’utilisateur courant à partir du token JWT

# Vérifie que l’utilisateur connecté est administrateur


# Création d’un nouvel exercice (réservé aux administrateurs)
@router.post("/", response_model=ExerciceResponse, status_code=201)
def create_exercice(exercice: ExerciceCreate, db: Session = Depends(get_db), user: dict = Depends(require_admin)):
    new_exercice = Exercice(**exercice.model_dump())
    db.add(new_exercice)
    db.commit()
    db.refresh(new_exercice)
    return new_exercice


# Récupération de tous les exercices
@router.get("/", response_model=list[ExerciceResponse])
def get_exercices(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(Exercice).all()


# Récupération d’un exercice par son identifiant
@router.get("/{exercice_id}", response_model=ExerciceResponse)
def get_exercice_by_id(
    exercice_id: int = Path(..., gt=0), db: Session = Depends(get_db), user: dict = Depends(get_current_user)
):
    exercice = db.query(Exercice).filter(Exercice.id_exercice == exercice_id).first()

    if exercice is None:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    return exercice


# Mise à jour d’un exercice existant (réservé aux administrateurs)
@router.put("/{exercice_id}", response_model=ExerciceResponse)
def update_exercice(
    exercice_id: int,
    exercice_update: ExerciceUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin),
):
    exercice = db.query(Exercice).filter(Exercice.id_exercice == exercice_id).first()

    if exercice is None:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    for key, value in exercice_update.model_dump(exclude_none=True).items():
        setattr(exercice, key, value)

    db.commit()
    db.refresh(exercice)
    return exercice


# Suppression d’un exercice (réservé aux administrateurs)
@router.delete("/{exercice_id}", status_code=204)
def delete_exercice(exercice_id: int, db: Session = Depends(get_db), user: dict = Depends(require_admin)):
    exercice = db.query(Exercice).filter(Exercice.id_exercice == exercice_id).first()

    if exercice is None:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    db.delete(exercice)
    db.commit()
