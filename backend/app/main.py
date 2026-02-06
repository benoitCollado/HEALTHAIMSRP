from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import SessionLocal
from app.models.utilisateur import Utilisateur
from app.security import create_access_token, verify_password
from app.routers import (
    utilisateurs,
    aliments,
    exercices,
    consommations,
    activites,
    metriques_sante,
    objectifs
)

app = FastAPI(title="HealthAI Coach API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.username == form_data.username
    ).first()

    if utilisateur is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, utilisateur.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(utilisateur.id_utilisateur),
        "is_admin": utilisateur.is_admin
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

app.include_router(utilisateurs.router)
app.include_router(aliments.router)
app.include_router(exercices.router)
app.include_router(consommations.router)
app.include_router(activites.router)
app.include_router(metriques_sante.router)
app.include_router(objectifs.router)
