from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.exercice import Exercice
from app.schemas.exercice import (
    ExerciceCreate,
    ExerciceResponse,
    ExerciceUpdate,
)
from app.security import verify_token

router = APIRouter(
    prefix="/exercices",
    tags=["Exercices"]
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

@router.post("/", response_model=ExerciceResponse, status_code=201)
def create_exercice(
    exercice: ExerciceCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    new_exercice = Exercice(**exercice.model_dump())
    db.add(new_exercice)
    db.commit()
    db.refresh(new_exercice)
    return new_exercice

@router.get("/", response_model=list[ExerciceResponse])
def get_exercices(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Exercice).all()

@router.get("/{exercice_id}", response_model=ExerciceResponse)
def get_exercice_by_id(
    exercice_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    exercice = db.query(Exercice).filter(
        Exercice.id_exercice == exercice_id
    ).first()

    if exercice is None:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    return exercice

@router.put("/{exercice_id}", response_model=ExerciceResponse)
def update_exercice(
    exercice_id: int,
    exercice_update: ExerciceUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    exercice = db.query(Exercice).filter(
        Exercice.id_exercice == exercice_id
    ).first()

    if exercice is None:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    for key, value in exercice_update.model_dump(exclude_none=True).items():
        setattr(exercice, key, value)

    db.commit()
    db.refresh(exercice)
    return exercice

@router.delete("/{exercice_id}", status_code=204)
def delete_exercice(
    exercice_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    exercice = db.query(Exercice).filter(
        Exercice.id_exercice == exercice_id
    ).first()

    if exercice is None:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    db.delete(exercice)
    db.commit()
