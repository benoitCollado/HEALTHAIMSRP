from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from models.objectif import Objectif
from schemas.objectif import (
    ObjectifCreate,
    ObjectifResponse,
    ObjectifUpdate,
)
from security import verify_token

router = APIRouter(
    prefix="/objectifs",
    tags=["Objectifs"]
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

@router.get("/", response_model=list[ObjectifResponse])
def get_objectifs(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Objectif).all()

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
