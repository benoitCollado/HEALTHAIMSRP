from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.aliment import Aliment
from app.schemas.aliment import (
    AlimentCreate,
    AlimentResponse,
    AlimentUpdate,
)
from app.security import verify_token

# Création du routeur pour les routes liées aux aliments
router = APIRouter(
    prefix="/aliments",
    tags=["Aliments"]
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

# Crée un nouvel aliment (réservé aux administrateurs)
@router.post("/", response_model=AlimentResponse, status_code=201)
def create_aliment(
    aliment: AlimentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    new_aliment = Aliment(**aliment.model_dump())
    db.add(new_aliment)
    db.commit()
    db.refresh(new_aliment)
    return new_aliment

# Récupère la liste de tous les aliments
@router.get("/", response_model=list[AlimentResponse])
def get_aliments(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Aliment).all()

# Récupère un aliment par son identifiant
@router.get("/{aliment_id}", response_model=AlimentResponse)
def get_aliment_by_id(
    aliment_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    aliment = db.query(Aliment).filter(
        Aliment.id_aliment == aliment_id
    ).first()

    if aliment is None:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")

    return aliment

# Met à jour un aliment existant (réservé aux administrateurs)
@router.put("/{aliment_id}", response_model=AlimentResponse)
def update_aliment(
    aliment_id: int,
    aliment_update: AlimentUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    aliment = db.query(Aliment).filter(
        Aliment.id_aliment == aliment_id
    ).first()

    if aliment is None:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")

    for key, value in aliment_update.model_dump(exclude_none=True).items():
        setattr(aliment, key, value)

    db.commit()
    db.refresh(aliment)
    return aliment

# Supprime un aliment (réservé aux administrateurs)
@router.delete("/{aliment_id}", status_code=204)
def delete_aliment(
    aliment_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    aliment = db.query(Aliment).filter(
        Aliment.id_aliment == aliment_id
    ).first()

    if aliment is None:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")

    db.delete(aliment)
    db.commit()
