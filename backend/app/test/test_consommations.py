import pytest
from datetime import date
from app.models.utilisateur import Utilisateur
from app.security import hash_password

_CONSOMMATION = {
    "date_consommation": "2026-01-15",
    "quantite_g": 150.0,
    "calories_calculees": 120.0,
    "id_aliment": 1,
    "id_utilisateur": 1,
}


@pytest.fixture
def user_headers(client, db_session):
    user = Utilisateur(
        username="usercons", password_hash=hash_password("pass"),
        age=25, sexe="H", taille_cm=175, poids_kg=70,
        niveau_activite=1, type_abonnement=1,
        date_inscription=date(2026, 1, 1), is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    r = client.post("/login", data={"username": "usercons", "password": "pass"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _create(client, headers):
    return client.post("/consommations/", json=_CONSOMMATION, headers=headers).json()


# ── CRUD ──────────────────────────────────────────────────────────────────────

def test_create_consommation(client, admin_headers):
    r = client.post("/consommations/", json=_CONSOMMATION, headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["quantite_g"] == 150.0


def test_get_consommations(client, admin_headers):
    r = client.get("/consommations/", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_consommation_by_id(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.get(f"/consommations/{created['id_consommation']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["id_consommation"] == created["id_consommation"]


def test_get_consommation_not_found(client, admin_headers):
    r = client.get("/consommations/99999", headers=admin_headers)
    assert r.status_code == 404


def test_update_consommation(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.put(
        f"/consommations/{created['id_consommation']}",
        json={"quantite_g": 200.0},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["quantite_g"] == 200.0


def test_update_consommation_not_found(client, admin_headers):
    r = client.put("/consommations/99999", json={"quantite_g": 50.0}, headers=admin_headers)
    assert r.status_code == 404


def test_delete_consommation(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.delete(f"/consommations/{created['id_consommation']}", headers=admin_headers)
    assert r.status_code == 204


def test_delete_consommation_not_found(client, admin_headers):
    r = client.delete("/consommations/99999", headers=admin_headers)
    assert r.status_code == 404


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_consommations_requires_auth(client):
    r = client.get("/consommations/")
    assert r.status_code == 401


def test_consommations_invalid_token(client):
    r = client.get("/consommations/", headers={"Authorization": "Bearer bad.token"})
    assert r.status_code == 401


def test_delete_consommation_non_admin(client, user_headers):
    r = client.delete("/consommations/99999", headers=user_headers)
    assert r.status_code == 403
