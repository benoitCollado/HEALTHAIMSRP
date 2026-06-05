import os
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp

# Clé secrète utilisée pour signer et vérifier les tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Vérification de la clé secrète
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# Algorithme de signature du JWT
ALGORITHM = "HS256"

# Durée de validité du token en minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 heures
TOTP_ISSUER = os.getenv("TOTP_ISSUER", "HealthAI MSPR")

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


def generate_totp_secret() -> str:
    """Generate a base32 secret compatible with Google Authenticator and Authy."""
    return pyotp.random_base32()


def build_totp_provisioning_uri(username: str, secret: str) -> str:
    """Return otpauth URI to enroll the account in authenticator applications."""
    return pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=TOTP_ISSUER)


def verify_totp_code(secret: str, code: str) -> bool:
    """Validate a 6-digit TOTP code with a small tolerance for clock drift."""
    if not secret or not code:
        return False
    normalized_code = code.strip().replace(" ", "")
    return pyotp.TOTP(secret).verify(normalized_code, valid_window=1)
