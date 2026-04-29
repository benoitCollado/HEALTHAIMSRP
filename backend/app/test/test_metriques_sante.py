import pytest
from datetime import date
from app.models.utilisateur import Utilisateur
from app.security import hash_password

_METRIQUE = {
    "date_mesure": "2026-01-15",
    "poids_kg": 75.0,
    "frequence_cardiaque": 65,
    "duree_sommeil_h": 7.5,
    "calories_brulees": 500,
    "pas": 8000,
    "id_utilisateur": 1,
}


@pytest.fixture
def user_headers(client, db_session):
    user = Utilisateur(
        username="usermet", password_hash=hash_password("pass"),
        age=30, sexe="H", taille_cm=180, poids_kg=80,
        niveau_activite=1, type_abonnement=1,
        date_inscription=date(2026, 1, 1), is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    r = client.post("/login", data={"username": "usermet", "password": "pass"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _create(client, headers):
    return client.post("/metriques-sante/", json=_METRIQUE, headers=headers).json()


# ── CRUD ──────────────────────────────────────────────────────────────────────

def test_create_metrique(client, admin_headers):
    r = client.post("/metriques-sante/", json=_METRIQUE, headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["poids_kg"] == 75.0


def test_get_metriques(client, admin_headers):
    r = client.get("/metriques-sante/", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_metrique_by_id(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.get(f"/metriques-sante/{created['id_metrique']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["id_metrique"] == created["id_metrique"]


def test_get_metrique_not_found(client, admin_headers):
    r = client.get("/metriques-sante/99999", headers=admin_headers)
    assert r.status_code == 404


def test_update_metrique(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.put(
        f"/metriques-sante/{created['id_metrique']}",
        json={"poids_kg": 74.0, "pas": 10000},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["poids_kg"] == 74.0
    assert r.json()["pas"] == 10000


def test_update_metrique_not_found(client, admin_headers):
    r = client.put("/metriques-sante/99999", json={"poids_kg": 70.0}, headers=admin_headers)
    assert r.status_code == 404


def test_delete_metrique(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.delete(f"/metriques-sante/{created['id_metrique']}", headers=admin_headers)
    assert r.status_code == 204


def test_delete_metrique_not_found(client, admin_headers):
    r = client.delete("/metriques-sante/99999", headers=admin_headers)
    assert r.status_code == 404


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_metriques_requires_auth(client):
    r = client.get("/metriques-sante/")
    assert r.status_code == 401


def test_metriques_invalid_token(client):
    r = client.get("/metriques-sante/", headers={"Authorization": "Bearer bad.token"})
    assert r.status_code == 401


def test_delete_metrique_non_admin(client, user_headers):
    r = client.delete("/metriques-sante/99999", headers=user_headers)
    assert r.status_code == 403
