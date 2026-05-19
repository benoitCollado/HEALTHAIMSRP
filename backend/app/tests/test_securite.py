def test_access_without_token(client):
    response = client.get("/utilisateurs")
    assert response.status_code == 401

def test_admin_only_delete(client, admin_headers):
    response = client.delete("/utilisateurs/999", headers=admin_headers)
    assert response.status_code in (204, 404)


# --- En-têtes de sécurité HTTP ---

def test_x_frame_options(client):
    response = client.get("/utilisateurs")
    assert response.headers.get("x-frame-options") == "DENY"

def test_x_content_type_options(client):
    response = client.get("/utilisateurs")
    assert response.headers.get("x-content-type-options") == "nosniff"

def test_x_xss_protection(client):
    response = client.get("/utilisateurs")
    assert response.headers.get("x-xss-protection") == "1; mode=block"

def test_strict_transport_security(client):
    response = client.get("/utilisateurs")
    hsts = response.headers.get("strict-transport-security", "")
    assert "max-age=31536000" in hsts
    assert "includeSubDomains" in hsts

def test_content_security_policy(client):
    response = client.get("/utilisateurs")
    csp = response.headers.get("content-security-policy", "")
    assert "default-src" in csp
    assert "frame-ancestors" in csp
