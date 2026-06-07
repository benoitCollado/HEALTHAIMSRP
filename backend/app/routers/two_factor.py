from app.dependencies import get_current_user, get_db
from app.models.utilisateur import Utilisateur
from app.schemas.two_factor import (
    TwoFactorCodeRequest,
    TwoFactorMessageResponse,
    TwoFactorSetupResponse,
    TwoFactorStatusResponse,
)
from app.security import build_totp_provisioning_uri, generate_totp_secret, verify_totp_code
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth/2fa", tags=["2FA"])


def _get_authenticated_user(db: Session, user_payload: dict) -> Utilisateur:
    sub = user_payload.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token payload") from exc

    utilisateur = db.query(Utilisateur).filter(Utilisateur.id_utilisateur == user_id).first()
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return utilisateur


@router.get("/status", response_model=TwoFactorStatusResponse)
def two_factor_status(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    utilisateur = _get_authenticated_user(db, user)
    return {"enabled": bool(utilisateur.totp_enabled)}


@router.post("/setup", response_model=TwoFactorSetupResponse)
def two_factor_setup(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    utilisateur = _get_authenticated_user(db, user)

    if utilisateur.totp_enabled:
        raise HTTPException(status_code=400, detail="2FA deja activee")

    secret = generate_totp_secret()
    utilisateur.totp_secret = secret
    utilisateur.totp_enabled = False
    db.commit()

    return {
        "enabled": False,
        "secret": secret,
        "provisioning_uri": build_totp_provisioning_uri(utilisateur.username, secret),
    }


@router.post("/enable", response_model=TwoFactorMessageResponse)
def two_factor_enable(
    payload: TwoFactorCodeRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    utilisateur = _get_authenticated_user(db, user)

    if not utilisateur.totp_secret:
        raise HTTPException(status_code=400, detail="Initialisez la 2FA avant activation")

    if not verify_totp_code(utilisateur.totp_secret, payload.code):
        raise HTTPException(status_code=400, detail="Code 2FA invalide")

    utilisateur.totp_enabled = True
    db.commit()

    return {"detail": "2FA activee", "enabled": True}


@router.post("/disable", response_model=TwoFactorMessageResponse)
def two_factor_disable(
    payload: TwoFactorCodeRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    utilisateur = _get_authenticated_user(db, user)

    if not utilisateur.totp_enabled:
        return {"detail": "2FA deja desactivee", "enabled": False}

    if not utilisateur.totp_secret or not verify_totp_code(utilisateur.totp_secret, payload.code):
        raise HTTPException(status_code=400, detail="Code 2FA invalide")

    utilisateur.totp_enabled = False
    utilisateur.totp_secret = None
    db.commit()

    return {"detail": "2FA desactivee", "enabled": False}
