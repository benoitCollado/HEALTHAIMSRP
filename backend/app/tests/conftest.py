import os
import sys
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

# Make imports work when tests are executed from the backend container root.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base
from app.main import app, get_db
from app.models.utilisateur import Utilisateur
from app.security import hash_password

# Tests use an in-memory SQLite database to avoid touching the real Neon DB.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class _ApiTestClient:
    """Préfixe automatiquement les chemins de test avec /api."""

    def __init__(self, client: TestClient):
        self._client = client

    def _path(self, url: str) -> str:
        if url.startswith("/api"):
            return url
        return f"/api{url}"

    def get(self, url: str, **kwargs):
        return self._client.get(self._path(url), **kwargs)

    def post(self, url: str, **kwargs):
        return self._client.post(self._path(url), **kwargs)

    def put(self, url: str, **kwargs):
        return self._client.put(self._path(url), **kwargs)

    def delete(self, url: str, **kwargs):
        return self._client.delete(self._path(url), **kwargs)

    def patch(self, url: str, **kwargs):
        return self._client.patch(self._path(url), **kwargs)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency overrides."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # All routers import the same get_db dependency, so one override is enough.
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield _ApiTestClient(c)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client, db_session):
    """Create an admin user and return a valid token."""
    # Seed admin user
    admin_user = Utilisateur(
        username="admin",
        password_hash=hash_password("admin123"),
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=1,
        type_abonnement=1,
        date_inscription=date(2026, 2, 5),
        is_admin=True,
    )
    db_session.add(admin_user)
    db_session.commit()

    response = client.post("/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
