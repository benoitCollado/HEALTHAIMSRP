def test_access_without_token(client):
    response = client.get("/utilisateurs")
    assert response.status_code == 401

def test_admin_only_delete(client, admin_headers):
    response = client.delete("/utilisateurs/999", headers=admin_headers)
    assert response.status_code in (204, 404)
