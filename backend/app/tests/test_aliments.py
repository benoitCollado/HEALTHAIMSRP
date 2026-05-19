def test_create_aliment_admin(client, admin_headers):
    data = {
        "nom_aliment": "Pomme",
        "calories": 52,
        "proteines_g": 0.3,
        "glucides_g": 14,
        "lipides_g": 0.2,
        "categorie": "Fruit"
    }

    response = client.post(
        "/aliments",
        json=data,
        headers=admin_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["nom_aliment"] == "Pomme"


def test_get_aliments(client, admin_headers):
    response = client.get(
        "/aliments",
        headers=admin_headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_aliment_not_found(client, admin_headers):
    response = client.delete(
        "/aliments/999",
        headers=admin_headers
    )

    assert response.status_code in (204, 404)
