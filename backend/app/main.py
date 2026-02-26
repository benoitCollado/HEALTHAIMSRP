from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
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

# Création de l'application FastAPI avec un titre
app = FastAPI(title="HealthAI Coach API")

# CORS : autoriser les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance pour fournir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        # Fournit la session à la route
        yield db
    finally:
        # Ferme la session après la requête
        db.close()

# Route de connexion utilisateur
@app.post("/login")
def login(
    # Récupère username et password depuis un formulaire OAuth2
    form_data: OAuth2PasswordRequestForm = Depends(),
    # Session de base de données
    db: Session = Depends(get_db)
):
    # Recherche de l’utilisateur par nom d’utilisateur
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.username == form_data.username
    ).first()

    # Si l’utilisateur n’existe pas
    if utilisateur is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Vérification du mot de passe
    if not verify_password(form_data.password, utilisateur.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Création du token JWT avec l’id utilisateur et le rôle admin
    token = create_access_token({
        "sub": str(utilisateur.id_utilisateur),
        "is_admin": utilisateur.is_admin
    })

    # Retour du token au client
    return {
        "access_token": token,
        "token_type": "bearer"
    }

# Enregistrement des routeurs dans l’application
app.include_router(utilisateurs.router)
app.include_router(aliments.router)
app.include_router(exercices.router)
app.include_router(consommations.router)
app.include_router(activites.router)
app.include_router(metriques_sante.router)
app.include_router(objectifs.router)
