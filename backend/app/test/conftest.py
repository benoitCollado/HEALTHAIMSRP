import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token(client):
    response = client.post(
        "/login",
        params={
            "username": "admin",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    return {
        "Authorization": f"Bearer {admin_token}"
    }
