import pytest
from datetime import date
from app.models.utilisateur import Utilisateur
from app.security import hash_password

_ACTIVITE = {
    "date_activite": "2026-01-15",
    "duree_minutes": 30,
    "calories_depensees": 200.0,
    "id_exercice": 1,
    "id_utilisateur": 1,
}


@pytest.fixture
def user_headers(client, db_session):
    user = Utilisateur(
        username="useract", password_hash=hash_password("pass"),
        age=25, sexe="F", taille_cm=165, poids_kg=60,
        niveau_activite=1, type_abonnement=1,
        date_inscription=date(2026, 1, 1), is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    r = client.post("/login", data={"username": "useract", "password": "pass"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _create(client, headers):
    return client.post("/activites/", json=_ACTIVITE, headers=headers).json()


# ── CRUD ──────────────────────────────────────────────────────────────────────

def test_create_activite(client, admin_headers):
    r = client.post("/activites/", json=_ACTIVITE, headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["duree_minutes"] == 30


def test_get_activites(client, admin_headers):
    r = client.get("/activites/", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_activite_by_id(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.get(f"/activites/{created['id_activite']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["id_activite"] == created["id_activite"]


def test_get_activite_not_found(client, admin_headers):
    r = client.get("/activites/99999", headers=admin_headers)
    assert r.status_code == 404


def test_update_activite(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.put(
        f"/activites/{created['id_activite']}",
        json={"duree_minutes": 60},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["duree_minutes"] == 60


def test_update_activite_not_found(client, admin_headers):
    r = client.put("/activites/99999", json={"duree_minutes": 60}, headers=admin_headers)
    assert r.status_code == 404


def test_delete_activite(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.delete(f"/activites/{created['id_activite']}", headers=admin_headers)
    assert r.status_code == 204


def test_delete_activite_not_found(client, admin_headers):
    r = client.delete("/activites/99999", headers=admin_headers)
    assert r.status_code == 404


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_activites_requires_auth(client):
    r = client.get("/activites/")
    assert r.status_code == 401


def test_activites_invalid_token(client):
    r = client.get("/activites/", headers={"Authorization": "Bearer invalid.token"})
    assert r.status_code == 401


def test_delete_activite_non_admin(client, user_headers):
    r = client.delete("/activites/99999", headers=user_headers)
    assert r.status_code == 403
