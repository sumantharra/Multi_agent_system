from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.models.user import User


def test_login_and_me(client: TestClient, db_session) -> None:
    db_session.add(
        User(
            email="admin@local.test",
            password_hash=hash_password("secret123"),
            role="owner",
            active=True,
        )
    )
    db_session.commit()

    bad = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@local.test", "password": "wrong"},
    )
    assert bad.status_code == 401

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@local.test", "password": "secret123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token

    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "admin@local.test"
    assert me.json()["role"] == "owner"


def test_brand_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/auth/brand")
    assert response.status_code == 200
    body = response.json()
    assert "name" in body
    assert "domain" in body
