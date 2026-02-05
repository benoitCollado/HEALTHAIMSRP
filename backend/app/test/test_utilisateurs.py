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
        "date_inscription": "2026-02-05"
    }

    response = client.post(
        "/utilisateurs",
        json=data,
        headers=admin_headers
    )

    assert response.status_code == 201
    assert response.json()["age"] == 25
