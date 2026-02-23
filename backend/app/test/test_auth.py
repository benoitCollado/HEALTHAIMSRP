from datetime import date
from app.models.utilisateur import Utilisateur
from app.security import hash_password


def test_login_ok(client, db_session):
    admin = Utilisateur(
        username="admin",
        password_hash=hash_password("admin123"),
        age=30,
        sexe="H",
        taille_cm=180,
        poids_kg=75,
        niveau_activite=1,
        type_abonnement=1,
        date_inscription=date.today(),
        is_admin=True
    )

    db_session.add(admin)
    db_session.commit()

    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "admin123"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    assert response.status_code == 200

    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
