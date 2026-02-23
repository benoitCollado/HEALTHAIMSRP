import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from datetime import date

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, get_db
from app.routers import utilisateurs
from app.database import Base
from app.models.utilisateur import Utilisateur
from app.security import hash_password

# Setup in-memory SQLite database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[utilisateurs.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
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
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()

    response = client.post(
        "/login",
        params={
            "username": "admin",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }
