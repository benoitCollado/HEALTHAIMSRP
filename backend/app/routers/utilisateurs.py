from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import (
    UtilisateurCreate,
    UtilisateurResponse,
    UtilisateurUpdate,
)
from app.security import verify_token, hash_password

router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"]
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


@router.post("/", response_model=UtilisateurResponse, status_code=201)
def create_utilisateur(
    utilisateur: UtilisateurCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    data = utilisateur.model_dump(exclude={"password"})
    data["password_hash"] = hash_password(utilisateur.password)

    new_user = Utilisateur(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=list[UtilisateurResponse])
def get_utilisateurs(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Utilisateur).all()

@router.get("/{utilisateur_id}", response_model=UtilisateurResponse)
def get_utilisateur_by_id(
    utilisateur_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.id_utilisateur == utilisateur_id
    ).first()

    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return utilisateur

@router.put("/{utilisateur_id}", response_model=UtilisateurResponse)
def update_utilisateur(
    utilisateur_id: int,
    utilisateur_update: UtilisateurUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.id_utilisateur == utilisateur_id
    ).first()

    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    for key, value in utilisateur_update.model_dump(exclude_none=True).items():
        setattr(utilisateur, key, value)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur

@router.delete("/{utilisateur_id}", status_code=204)
def delete_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.id_utilisateur == utilisateur_id
    ).first()

    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    db.delete(utilisateur)
    db.commit()
