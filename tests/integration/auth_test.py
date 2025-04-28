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
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
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
