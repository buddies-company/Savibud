from fastapi.testclient import TestClient

from drivers.main import app

client = TestClient(app)


def test_user_me(jwt_token):
    """Retrive tesst user info with success"""
    response = client.get("/users/me", headers={"Authorization": f"Bearer {jwt_token}"})
    assert response.status_code == 200
    assert response.json() == {
        "id": None,
        "username": "johndoe",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    }


def test_old_token():
    """Use old provided JWT token"""
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwidXNlcl9pZCI6bnVsbCwiZXhwIjoxNzQ1NTkzNzMzfQ.hUPwt16Q0GSn5mEiniBmpfvFSu5yMuX-JJu99BD77eY"
        },
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "token has been expired"}


def test_bad_token():
    """Use invalid JWT token"""
    response = client.get(
        "/users/me",
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwidXNlcl9pZCI6bnVdxhwiZXhwIjoxNzQ1NTkzNzMzfQ.hUPwt16Q0GSn5mEiniBmpfvFSu5yMuX-JJu99BD77eY"
        },
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_register_and_login_and_get_me():
    # Register a new user
    register_payload = {"username": "janedoe", "password": "securepassword"}
    response = client.post("/auth/register", json=register_payload)
    assert response.status_code == 201
    assert response.json()["username"] == "janedoe"

    # Login with the new user
    login_payload = {"username": "janedoe", "password": "securepassword"}
    response = client.post("/token", data=login_payload)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Get user info with the token
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "janedoe"


def test_register_existing_user():
    # Try to register the same user twice
    payload = {"username": "janedoe", "password": "securepassword"}
    response1 = client.post("/auth/register", json=payload)
    response2 = client.post("/auth/register", json=payload)
    assert response2.status_code == 409 or response2.status_code == 400


def test_password_is_hashed_after_registration():
    """Ensure that the password is hashed after user registration"""
    payload = {"username": "hashcheckuser", "password": "plainpassword"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    # The password in the response should not be the same as the plain password
    assert data["password"] != payload["password"]
    # The password should look like a bcrypt hash
    assert data["password"].startswith("$2b$")
