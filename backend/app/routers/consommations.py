from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.consommation import Consommation
from app.schemas.consommation import (
    ConsommationCreate,
    ConsommationResponse,
    ConsommationUpdate,
)
from app.security import verify_token

# Création du routeur pour les routes liées aux consommations
router = APIRouter(
    prefix="/consommations",
    tags=["Consommations"]
)

# Schéma OAuth2 pour récupérer le token depuis l’endpoint /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dépendance pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Récupère l’utilisateur courant à partir du token JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

# Vérifie que l’utilisateur est administrateur
def require_admin(user: dict = Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin only")
    return user

# Crée une nouvelle consommation pour un utilisateur connecté
@router.post("/", response_model=ConsommationResponse, status_code=201)
def create_consommation(
    consommation: ConsommationCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    new_consommation = Consommation(**consommation.model_dump())
    db.add(new_consommation)
    db.commit()
    db.refresh(new_consommation)
    return new_consommation

# Récupère la liste de toutes les consommations
@router.get("/", response_model=list[ConsommationResponse])
def get_consommations(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Consommation).all()

# Récupère une consommation par son identifiant
@router.get("/{consommation_id}", response_model=ConsommationResponse)
def get_consommation_by_id(
    consommation_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    consommation = db.query(Consommation).filter(
        Consommation.id_consommation == consommation_id
    ).first()

    if consommation is None:
        raise HTTPException(status_code=404, detail="Consommation non trouvée")

    return consommation

# Met à jour une consommation existante
@router.put("/{consommation_id}", response_model=ConsommationResponse)
def update_consommation(
    consommation_id: int,
    consommation_update: ConsommationUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    consommation = db.query(Consommation).filter(
        Consommation.id_consommation == consommation_id
    ).first()

    if consommation is None:
        raise HTTPException(status_code=404, detail="Consommation non trouvée")

    for key, value in consommation_update.model_dump(exclude_none=True).items():
        setattr(consommation, key, value)

    db.commit()
    db.refresh(consommation)
    return consommation

# Supprime une consommation (réservé aux administrateurs)
@router.delete("/{consommation_id}", status_code=204)
def delete_consommation(
    consommation_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    consommation = db.query(Consommation).filter(
        Consommation.id_consommation == consommation_id
    ).first()

    if consommation is None:
        raise HTTPException(status_code=404, detail="Consommation non trouvée")

    db.delete(consommation)
    db.commit()
