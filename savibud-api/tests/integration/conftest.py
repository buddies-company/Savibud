import pytest
from fastapi.testclient import TestClient

from drivers.main import app

client = TestClient(app)


@pytest.fixture(scope="session")
def jwt_token():
    """Retrieve test user JWT token"""
    response = client.post("/token", data={"username": "johndoe", "password": "secret"})
    assert response.status_code == 200
    return response.json()["access_token"]
