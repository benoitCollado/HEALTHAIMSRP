import time
from datetime import date

from app.models.utilisateur import Utilisateur
from app.security import _totp_at, generate_totp_secret, hash_password


def test_login_ok(client, db_session):
    admin = Utilisateur(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=1,
        type_abonnement=1,
        date_inscription=date.today(),
        is_admin=True,
    )

    db_session.add(admin)
    db_session.commit()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_two_factor_status_endpoint(client, db_session):
    user = Utilisateur(
        username="user2fa",
        email="user2fa@example.com",
        password_hash=hash_password("pass123"),
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=1,
        type_abonnement=1,
        date_inscription=date.today(),
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()

    login = client.post("/login", data={"username": "user2fa", "password": "pass123"})
    token = login.json()["access_token"]

    response = client.get("/auth/2fa/status", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {"enabled": False}


def test_public_register_endpoint_is_not_shadowed_by_user_id_route(client):
    response = client.post(
        "/utilisateurs/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "pass123",
            "age": 28,
            "sexe": "F",
            "taille_cm": 168,
            "poids_kg": 62,
            "niveau_activite": 3,
            "type_abonnement": 1,
            "date_inscription": date.today().isoformat(),
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_login_requires_valid_otp_when_two_factor_enabled(client, db_session):
    secret = generate_totp_secret()
    user = Utilisateur(
        username="secureuser",
        email="secureuser@example.com",
        password_hash=hash_password("pass123"),
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=1,
        type_abonnement=1,
        date_inscription=date.today(),
        is_admin=False,
        totp_secret=secret,
        totp_enabled=True,
    )
    db_session.add(user)
    db_session.commit()

    missing_otp = client.post("/login", data={"username": "secureuser", "password": "pass123"})
    valid_otp = client.post(
        "/login",
        data={
            "username": "secureuser",
            "password": "pass123",
            "otp": _totp_at(secret, int(time.time() // 30)),
        },
    )

    assert missing_otp.status_code == 401
    assert missing_otp.json()["detail"] == "Code 2FA requis"
    assert valid_otp.status_code == 200


def test_openapi_uses_public_api_prefix(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["servers"] == [{"url": "/api"}]
    assert (
        schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"]["tokenUrl"] == "/api/login"
    )
