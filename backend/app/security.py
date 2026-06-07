import base64
import hashlib
import hmac
import os
import secrets
import struct
import time
from datetime import datetime, timedelta
from urllib.parse import quote

from jose import JWTError, jwt
from passlib.context import CryptContext

# Clé secrète utilisée pour signer et vérifier les tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Vérification de la clé secrète
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

# Algorithme de signature du JWT
ALGORITHM = "HS256"

# Durée de validité du token en minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 heures

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
    """Generate a base32 secret compatible with authenticator apps."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def build_totp_provisioning_uri(username: str, secret: str, issuer: str = "HealthAI MSPR") -> str:
    """Build the otpauth URI used by Google Authenticator/Authy."""
    label = quote(f"{issuer}:{username}")
    issuer_q = quote(issuer)
    return f"otpauth://totp/{label}?secret={secret}&issuer={issuer_q}&algorithm=SHA1&digits=6&period=30"


def _totp_at(secret: str, counter: int, digits: int = 6) -> str:
    padded_secret = secret.upper() + "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(padded_secret)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**digits)).zfill(digits)


def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """Verify a 6-digit TOTP code, accepting one time step of clock drift."""
    normalized = "".join(ch for ch in code.strip() if ch.isdigit())
    if len(normalized) != 6:
        return False

    counter = int(time.time() // 30)
    return any(
        hmac.compare_digest(_totp_at(secret, counter + drift), normalized) for drift in range(-window, window + 1)
    )
