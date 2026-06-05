from app.database import SessionLocal
from app.security import verify_token
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    """Provide one SQLAlchemy session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decode the Bearer token and expose its JWT payload to protected routes."""
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def require_admin(user: dict = Depends(get_current_user)):
    """Guard routes that must only be available to administrator accounts."""
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin only")
    return user
