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

# Routeur pour les endpoints liés aux utilisateurs
router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"]
)

# Schéma OAuth2 pour récupérer le token JWT depuis /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dépendance pour gérer la session de base de données
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

# Vérifie que l’utilisateur courant est administrateur
def require_admin(user: dict = Depends(get_current_user)):
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin only")
    return user

# Création d’un nouvel utilisateur (admin uniquement)
@router.post("/", response_model=UtilisateurResponse, status_code=201)
def create_utilisateur(
    utilisateur: UtilisateurCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_admin)
):
    # Conversion du schéma Pydantic en dictionnaire sans le mot de passe
    data = utilisateur.model_dump(exclude={"password"})
    # Hash du mot de passe avant stockage
    data["password_hash"] = hash_password(utilisateur.password)

    # Création de l’entité utilisateur SQLAlchemy
    new_user = Utilisateur(**data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Récupération de tous les utilisateurs
@router.get("/", response_model=list[UtilisateurResponse])
def get_utilisateurs(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    return db.query(Utilisateur).all()

# Récupération d’un utilisateur par identifiant
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

# Mise à jour d’un utilisateur existant (admin uniquement)
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

    # Mise à jour uniquement des champs fournis
    for key, value in utilisateur_update.model_dump(exclude_none=True).items():
        setattr(utilisateur, key, value)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur

# Suppression d’un utilisateur (admin uniquement)
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


# ============================================================
# Route publique d'inscription - Accessible à tous (sans token)
# ============================================================

@router.post("/register", response_model=UtilisateurResponse, status_code=201)
def register(
    utilisateur: UtilisateurCreate,
    db: Session = Depends(get_db)
):
    """
    Route publique permettant à un nouvel utilisateur de créer un compte.
    Cette route est accessible sans authentification (pas de token requis).
    
    Étapes du processus d'inscription :
    1. Vérifier que le nom d'utilisateur n'existe pas déjà
    2. Hasher le mot de passe pour le stocker de manière sécurisée
    3. Créer l'utilisateur avec is_admin = False par défaut
    4. Sauvegarder dans la base de données
    """
    
    # Vérification si le nom d'utilisateur existe déjà dans la base de données
    # Si un utilisateur avec le même username existe, on retourne une erreur 400
    existing_user = db.query(Utilisateur).filter(
        Utilisateur.username == utilisateur.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Ce nom d'utilisateur est déjà utilisé"
        )
    
    # Conversion du schéma Pydantic en dictionnaire
    # On exclut le mot de passe car on va le hasher séparément
    data = utilisateur.model_dump(exclude={"password"})
    
    # Hashage du mot de passe avec bcrypt pour le sécuriser
    # Le mot de passe en clair n'est jamais stocké dans la base de données
    data["password_hash"] = hash_password(utilisateur.password)
    
    # Création du nouvel utilisateur
    # Le champ is_admin sera automatiquement False (valeur par défaut du modèle)
    new_user = Utilisateur(**data)
    
    # Ajout à la session SQLAlchemy et commit pour sauvegarder
    db.add(new_user)
    db.commit()
    
    # Rafraîchir l'objet pour obtenir l'ID généré par la base de données
    db.refresh(new_user)
    
    # Retourner l'utilisateur créé (sans le mot de passe hashé)
    return new_user
