import asyncio

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.security import OAuth2PasswordRequestForm

from app.database import SessionLocal, engine
from app.observability.email_alert import send_error_alert
from app.observability.logger import get_logger
from app.middleware import SecurityHeadersMiddleware, RequestLoggingMiddleware
from app.observability.monitoring import metrics
from app.models.utilisateur import Utilisateur
from app.security import create_access_token, verify_password
from app.routers import (
    utilisateurs,
    aliments,
    exercices,
    consommations,
    activites,
    metriques_sante,
    objectifs,
    admin,
)

_log = get_logger("main")

app = FastAPI(title="HealthAI Coach API")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    _log.error("500 %s %s — %s: %s", request.method, request.url.path, type(exc).__name__, exc)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        None,
        send_error_alert,
        exc,
        request.method,
        str(request.url),
        None,
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", tags=["monitoring"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        _log.warning("Health check DB failed: %s", e)
        db_status = "error"

    status = "ok" if db_status == "ok" else "degraded"
    return {"status": status, "database": db_status}


@app.get("/metrics", tags=["monitoring"])
def get_metrics():
    return metrics.snapshot()


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    utilisateur = db.query(Utilisateur).filter(
        Utilisateur.username == form_data.username
    ).first()

    if utilisateur is None:
        _log.warning("Login failed — user not found: %s", form_data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, utilisateur.password_hash):
        _log.warning("Login failed — wrong password: %s", form_data.username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(utilisateur.id_utilisateur),
        "is_admin": utilisateur.is_admin,
    })
    _log.info("Login OK — user %s (admin=%s)", utilisateur.username, utilisateur.is_admin)
    return {"access_token": token, "token_type": "bearer"}


app.include_router(utilisateurs.router)
app.include_router(aliments.router)
app.include_router(exercices.router)
app.include_router(consommations.router)
app.include_router(activites.router)
app.include_router(metriques_sante.router)
app.include_router(objectifs.router)
app.include_router(admin.router)
