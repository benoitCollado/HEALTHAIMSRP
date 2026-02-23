def test_create_exercice_admin(client, admin_headers):
    data = {
        "nom_exercice": "Pompes",
        "type_exercice": "Musculation",
        "niveau_difficulte": "Facile",
        "equipement": "Aucun",
        "muscle_principal": "Pectoraux"
    }

    response = client.post(
        "/exercices",
        json=data,
        headers=admin_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["nom_exercice"] == "Pompes"


def test_get_exercices(client, admin_headers):
    response = client.get(
        "/exercices",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_exercice_not_found(client, admin_headers):
    response = client.get(
        "/exercices/999",
        headers=admin_headers
    )

    assert response.status_code == 404
