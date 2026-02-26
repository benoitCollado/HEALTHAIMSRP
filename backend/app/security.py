import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

# Clé secrète utilisée pour signer et vérifier les tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY") or "healthaim-secret-key-dev-change-in-production"

# Algorithme de signature du JWT
ALGORITHM = "HS256"

# Durée de validité du token en minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration du contexte de hash pour les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash un mot de passe en clair
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Vérifie un mot de passe en clair par rapport à son hash
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

# Crée un token JWT avec une date d’expiration
def create_access_token(data: dict):
    # Copie des données à encoder dans le token
    to_encode = data.copy()

    # Calcul de la date d’expiration
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Ajout de l’expiration dans le payload
    to_encode.update({"exp": expire})

    # Génération et signature du token JWT
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Vérifie et décode un token JWT
def verify_token(token: str):
    try:
        # Décodage du token avec la clé secrète
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Token invalide ou expiré
        return None
