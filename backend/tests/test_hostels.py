from fastapi.testclient import TestClient


def test_hostel_crud_flow(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/hostels",
        json={
            "name": "Sai Boys Hostel",
            "code": "sai-01",
            "address": "MG Road",
            "contact_name": "Ravi",
            "phone": "9999999999",
            "default_rate_per_liter": "45.50",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Sai Boys Hostel"
    assert created["code"] == "SAI-01"
    assert created["active"] is True
    hostel_id = created["id"]

    list_response = client.get("/api/v1/hostels")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed["total"] == 1
    assert listed["items"][0]["id"] == hostel_id

    get_response = client.get(f"/api/v1/hostels/{hostel_id}")
    assert get_response.status_code == 200
    assert get_response.json()["code"] == "SAI-01"

    update_response = client.put(
        f"/api/v1/hostels/{hostel_id}",
        json={"default_rate_per_liter": "50.00", "contact_name": "Anita"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["default_rate_per_liter"] == "50.00"
    assert updated["contact_name"] == "Anita"

    delete_response = client.delete(f"/api/v1/hostels/{hostel_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["active"] is False

    active_list = client.get("/api/v1/hostels", params={"active": True})
    assert active_list.status_code == 200
    assert active_list.json()["total"] == 0


def test_duplicate_hostel_code_conflict(client: TestClient) -> None:
    payload = {
        "name": "Alpha Hostel",
        "code": "alpha",
        "default_rate_per_liter": "40.00",
    }
    assert client.post("/api/v1/hostels", json=payload).status_code == 201

    duplicate = client.post(
        "/api/v1/hostels",
        json={
            "name": "Alpha Hostel 2",
            "code": "ALPHA",
            "default_rate_per_liter": "41.00",
        },
    )
    assert duplicate.status_code == 409
    body = duplicate.json()
    assert body["error"]["code"] == "CONFLICT"
    assert body["error"]["details"][0]["field"] == "code"


def test_hostels_require_auth_gate_when_disabled(client: TestClient) -> None:
    from app.core.config import Settings, get_settings
    from app.main import app as fastapi_app

    app_settings = Settings(
        app_env="development",
        allow_unauthenticated=False,
        database_url="sqlite:///:memory:",
    )

    fastapi_app.dependency_overrides[get_settings] = lambda: app_settings
    response = client.get("/api/v1/hostels")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
