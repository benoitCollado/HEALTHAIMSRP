import asyncio

from app.dependencies import get_db, require_admin
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.models.utilisateur import Utilisateur
from app.observability.email_alert import send_error_alert
from app.observability.logger import get_logger
from app.observability.monitoring import metrics
from app.routers import (
    activites,
    admin,
    aliments,
    consommations,
    exercices,
    metriques_sante,
    objectifs,
    utilisateurs,
)
from app.security import create_access_token, verify_password, verify_token
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

_log = get_logger("main")

app = FastAPI(title="HealthAI Coach API")
api_router = APIRouter(prefix="/api")


def _get_request_user_id(request: Request):
    """Best-effort user extraction for logs and alert emails."""
    auth = request.headers.get("authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    sub = payload.get("sub")
    try:
        return int(sub)
    except (TypeError, ValueError):
        return sub


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Unhandled errors are logged with their traceback, then the admin alert is
    # sent in a thread so the HTTP response is not blocked by SMTP latency.
    user_id = _get_request_user_id(request)
    _log.error(
        "500 %s %s - %s: %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        exc,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        None,
        send_error_alert,
        exc,
        request.method,
        str(request.url),
        user_id,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur."},
    )


app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@api_router.get("/health", tags=["monitoring"])
def health(db: Session = Depends(get_db)):
    """Health endpoint used by operators to verify API and database availability."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        _log.warning("Health check DB failed: %s", e)
        db_status = "error"

    status = "ok" if db_status == "ok" else "degraded"
    return {"status": status, "database": db_status}


@api_router.get("/metrics", tags=["monitoring"])
def get_metrics(user: dict = Depends(require_admin)):
    """Return in-memory request metrics. This endpoint is admin-only."""
    return metrics.snapshot()


@api_router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate a user and return the JWT used by protected endpoints."""
    try:
        utilisateur = db.query(Utilisateur).filter(Utilisateur.username == form_data.username).first()
    except SQLAlchemyError as exc:
        _log.error("Login failed - database unavailable: %s", exc)
        raise HTTPException(status_code=503, detail="Base de donnees indisponible") from exc

    if utilisateur is None:
        _log.warning("Login failed - user not found: %s", form_data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, utilisateur.password_hash):
        _log.warning("Login failed - wrong password: %s", form_data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {
            "sub": str(utilisateur.id_utilisateur),
            "is_admin": utilisateur.is_admin,
        }
    )
    _log.info("Login OK - user %s (admin=%s)", utilisateur.username, utilisateur.is_admin)
    return {"access_token": token, "token_type": "bearer"}


api_router.include_router(utilisateurs.router)
api_router.include_router(aliments.router)
api_router.include_router(exercices.router)
api_router.include_router(consommations.router)
api_router.include_router(activites.router)
api_router.include_router(metriques_sante.router)
api_router.include_router(objectifs.router)
api_router.include_router(admin.router)

app.include_router(api_router)
