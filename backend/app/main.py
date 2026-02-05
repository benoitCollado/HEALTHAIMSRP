
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal
from models.utilisateur import Utilisateur
from security import create_access_token, verify_password
from routers import (
    utilisateurs,
    aliments,
    exercices,
    consommations,
    activites,
    metriques_sante,
    objectifs
)


app = FastAPI(title="HealthAI Coach API")

# Autorise le frontend local (Vite) à accéder à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(utilisateur_id: int, db: Session = Depends(get_db)):
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.id_utilisateur == utilisateur_id
    ).first()

    if utilisateur is None:
        raise HTTPException(status_code=401, detail="Utilisateur inconnu")

    if not verify_password(password, utilisateur.password_hash):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    access_token = create_access_token({
        "sub": utilisateur.id_utilisateur,
        "is_admin": utilisateur.is_admin
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

app.include_router(utilisateurs.router)
app.include_router(aliments.router)
app.include_router(exercices.router)
app.include_router(consommations.router)
app.include_router(activites.router)
app.include_router(metriques_sante.router)
app.include_router(objectifs.router)
