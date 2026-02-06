from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.activite import Activite
from app.schemas.activite import (
    ActiviteCreate,
    ActiviteResponse,
    ActiviteUpdate,
)
from app.security import verify_token

# Création du routeur pour les routes liées aux activités
router = APIRouter(
    prefix="/activites",
    tags=["Activites"]
)

# Schéma d’authentification OAuth2 basé sur un token
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

# Crée une nouvelle activité
@router.post("/", response_model=ActiviteResponse, status_code=201)
def create_activite(
    activite: ActiviteCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    new_activite = Activite(**activite.model_dump())
    db.add(new_activite)
    db.commit()
    db.refresh(new_activite)
    return new_activite

# Récupère toutes les activités
@router.get("/", response_model=list[ActiviteResponse])
def get_activites(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Activite).all()

# Récupère une activité par son identifiant
@router.get("/{activite_id}", response_model=ActiviteResponse)
def get_activite_by_id(
    activite_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    activite = db.query(Activite).filter(
        Activite.id_activite == activite_id
    ).first()

    if activite is None:
        raise HTTPException(status_code=404, detail="Activite non trouvée")

    return activite

# Met à jour une activité existante
@router.put("/{activite_id}", response_model=ActiviteResponse)
def update_activite(
    activite_id: int,
    activite_update: ActiviteUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    activite = db.query(Activite).filter(
        Activite.id_activite == activite_id
    ).first()

    if activite is None:
        raise HTTPException(status_code=404, detail="Activite non trouvée")

    for key, value in activite_update.model_dump(exclude_none=True).items():
        setattr(activite, key, value)

    db.commit()
    db.refresh(activite)
    return activite

# Supprime une activité (réservé aux administrateurs)
@router.delete("/{activite_id}", status_code=204)
def delete_activite(
    activite_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    activite = db.query(Activite).filter(
        Activite.id_activite == activite_id
    ).first()

    if activite is None:
        raise HTTPException(status_code=404, detail="Activite non trouvée")

    db.delete(activite)
    db.commit()
