import pytest
from datetime import date
from app.models.utilisateur import Utilisateur
from app.security import hash_password

_OBJECTIF = {
    "type_objectif": "perte_poids",
    "description": "Perdre 5 kg en 3 mois",
    "date_debut": "2026-01-01",
    "date_fin": "2026-03-31",
    "statut": "en_cours",
    "id_utilisateur": 1,
}


@pytest.fixture
def user_headers(client, db_session):
    user = Utilisateur(
        username="userobj", password_hash=hash_password("pass"),
        age=28, sexe="F", taille_cm=170, poids_kg=65,
        niveau_activite=2, type_abonnement=1,
        date_inscription=date(2026, 1, 1), is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    r = client.post("/login", data={"username": "userobj", "password": "pass"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _create(client, headers):
    return client.post("/objectifs/", json=_OBJECTIF, headers=headers).json()


# ── CRUD ──────────────────────────────────────────────────────────────────────

def test_create_objectif(client, admin_headers):
    r = client.post("/objectifs/", json=_OBJECTIF, headers=admin_headers)
    assert r.status_code == 201
    assert r.json()["type_objectif"] == "perte_poids"


def test_get_objectifs(client, admin_headers):
    r = client.get("/objectifs/", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_objectif_by_id(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.get(f"/objectifs/{created['id_objectif']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["id_objectif"] == created["id_objectif"]


def test_get_objectif_not_found(client, admin_headers):
    r = client.get("/objectifs/99999", headers=admin_headers)
    assert r.status_code == 404


def test_update_objectif(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.put(
        f"/objectifs/{created['id_objectif']}",
        json={"statut": "termine", "description": "Objectif atteint"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["statut"] == "termine"


def test_update_objectif_not_found(client, admin_headers):
    r = client.put("/objectifs/99999", json={"statut": "termine"}, headers=admin_headers)
    assert r.status_code == 404


def test_delete_objectif(client, admin_headers):
    created = _create(client, admin_headers)
    r = client.delete(f"/objectifs/{created['id_objectif']}", headers=admin_headers)
    assert r.status_code == 204


def test_delete_objectif_not_found(client, admin_headers):
    r = client.delete("/objectifs/99999", headers=admin_headers)
    assert r.status_code == 404


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_objectifs_requires_auth(client):
    r = client.get("/objectifs/")
    assert r.status_code == 401


def test_objectifs_invalid_token(client):
    r = client.get("/objectifs/", headers={"Authorization": "Bearer bad.token"})
    assert r.status_code == 401


def test_delete_objectif_non_admin(client, user_headers):
    r = client.delete("/objectifs/99999", headers=user_headers)
    assert r.status_code == 403
