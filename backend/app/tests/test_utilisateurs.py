def test_get_utilisateurs(client, admin_headers):
    response = client.get("/utilisateurs", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_utilisateur_by_id(client, admin_headers):
    response = client.get("/utilisateurs/1", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id_utilisateur"] == 1


def test_get_utilisateur_not_found(client, admin_headers):
    response = client.get("/utilisateurs/999", headers=admin_headers)
    assert response.status_code == 404


def test_create_utilisateur(client, admin_headers):
    data = {
        "age": 25,
        "sexe": "H",
        "taille_cm": 180,
        "poids_kg": 75,
        "niveau_activite": 2,
        "type_abonnement": 1,
        "date_inscription": "2026-02-05",
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpassword",
    }

    response = client.post("/utilisateurs", json=data, headers=admin_headers)

    assert response.status_code == 201
    assert response.json()["age"] == 25
    assert response.json()["email"] == "testuser@example.com"


def test_create_utilisateur_rejects_duplicate_email(client, admin_headers):
    first = {
        "age": 25,
        "sexe": "H",
        "taille_cm": 180,
        "poids_kg": 75,
        "niveau_activite": 2,
        "type_abonnement": 1,
        "date_inscription": "2026-02-05",
        "username": "emailuser1",
        "email": "same@example.com",
        "password": "testpassword",
    }
    second = {
        **first,
        "username": "emailuser2",
    }

    assert client.post("/utilisateurs", json=first, headers=admin_headers).status_code == 201

    response = client.post("/utilisateurs", json=second, headers=admin_headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Cette adresse mail est deja utilisee"
