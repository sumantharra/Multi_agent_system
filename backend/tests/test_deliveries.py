from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient


def _create_hostel(
    client: TestClient,
    *,
    code: str = "sai-01",
    rate: str = "45.50",
) -> str:
    response = client.post(
        "/api/v1/hostels",
        json={
            "name": f"Hostel {code}",
            "code": code,
            "default_rate_per_liter": rate,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_delivery_computes_total_and_copies_rate(client: TestClient) -> None:
    hostel_id = _create_hostel(client)
    response = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_id,
            "delivery_date": "2026-07-01",
            "morning_quantity": "12.500",
            "evening_quantity": "10.250",
            "notes": "First day",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["hostel_id"] == hostel_id
    assert body["delivery_date"] == "2026-07-01"
    assert Decimal(body["morning_quantity"]) == Decimal("12.500")
    assert Decimal(body["evening_quantity"]) == Decimal("10.250")
    assert Decimal(body["total_quantity"]) == Decimal("22.750")
    assert Decimal(body["rate_per_liter"]) == Decimal("45.50")
    assert body["notes"] == "First day"
    assert body["created_by"] is None


def test_explicit_rate_does_not_change_hostel_default(client: TestClient) -> None:
    hostel_id = _create_hostel(client, rate="45.50")
    response = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_id,
            "delivery_date": "2026-07-02",
            "morning_quantity": "8",
            "evening_quantity": "7",
            "rate_per_liter": "60.00",
        },
    )
    assert response.status_code == 201
    assert Decimal(response.json()["rate_per_liter"]) == Decimal("60.00")

    hostel = client.get(f"/api/v1/hostels/{hostel_id}")
    assert hostel.status_code == 200
    assert Decimal(hostel.json()["default_rate_per_liter"]) == Decimal("45.50")


def test_duplicate_hostel_date_conflict(client: TestClient) -> None:
    hostel_id = _create_hostel(client)
    payload = {
        "hostel_id": hostel_id,
        "delivery_date": "2026-07-03",
        "morning_quantity": "5",
        "evening_quantity": "5",
    }
    assert client.post("/api/v1/deliveries", json=payload).status_code == 201

    duplicate = client.post("/api/v1/deliveries", json=payload)
    assert duplicate.status_code == 409
    body = duplicate.json()
    assert body["error"]["code"] == "CONFLICT"
    assert body["error"]["details"][0]["field"] == "delivery_date"


def test_unknown_hostel_not_found(client: TestClient) -> None:
    response = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": str(uuid4()),
            "delivery_date": "2026-07-04",
            "morning_quantity": "1",
            "evening_quantity": "1",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_inactive_hostel_not_found(client: TestClient) -> None:
    hostel_id = _create_hostel(client, code="old-01")
    assert client.delete(f"/api/v1/hostels/{hostel_id}").status_code == 200

    response = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_id,
            "delivery_date": "2026-07-05",
            "morning_quantity": "1",
            "evening_quantity": "1",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_list_filters_by_hostel_and_date_range(client: TestClient) -> None:
    sai = _create_hostel(client, code="sai-01")
    alpha = _create_hostel(client, code="alpha")

    for day, hostel_id in (
        ("2026-07-01", sai),
        ("2026-07-15", sai),
        ("2026-07-31", sai),
        ("2026-07-15", alpha),
    ):
        created = client.post(
            "/api/v1/deliveries",
            json={
                "hostel_id": hostel_id,
                "delivery_date": day,
                "morning_quantity": "4",
                "evening_quantity": "6",
            },
        )
        assert created.status_code == 201

    sai_july = client.get(
        "/api/v1/deliveries",
        params={"hostel_id": sai, "from": "2026-07-01", "to": "2026-07-15"},
    )
    assert sai_july.status_code == 200
    listed = sai_july.json()
    assert listed["total"] == 2
    dates = {item["delivery_date"] for item in listed["items"]}
    assert dates == {"2026-07-01", "2026-07-15"}
    assert all(item["hostel_id"] == sai for item in listed["items"])


def test_get_and_update_recomputes_total(client: TestClient) -> None:
    hostel_id = _create_hostel(client)
    created = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_id,
            "delivery_date": "2026-07-10",
            "morning_quantity": "3",
            "evening_quantity": "2",
        },
    )
    assert created.status_code == 201
    delivery_id = created.json()["id"]

    fetched = client.get(f"/api/v1/deliveries/{delivery_id}")
    assert fetched.status_code == 200
    assert Decimal(fetched.json()["total_quantity"]) == Decimal(5)

    updated = client.put(
        f"/api/v1/deliveries/{delivery_id}",
        json={"morning_quantity": "9.000", "evening_quantity": "1.500"},
    )
    assert updated.status_code == 200
    body = updated.json()
    assert Decimal(body["morning_quantity"]) == Decimal("9.000")
    assert Decimal(body["evening_quantity"]) == Decimal("1.500")
    assert Decimal(body["total_quantity"]) == Decimal("10.500")


def test_get_missing_delivery_not_found(client: TestClient) -> None:
    response = client.get(f"/api/v1/deliveries/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_negative_quantity_rejected(client: TestClient) -> None:
    hostel_id = _create_hostel(client)
    response = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_id,
            "delivery_date": "2026-07-11",
            "morning_quantity": "-1",
            "evening_quantity": "2",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_deliveries_require_auth_gate_when_disabled(client: TestClient) -> None:
    from app.core.config import Settings, get_settings
    from app.main import app as fastapi_app

    app_settings = Settings(
        app_env="development",
        allow_unauthenticated=False,
        database_url="sqlite:///:memory:",
    )

    fastapi_app.dependency_overrides[get_settings] = lambda: app_settings
    response = client.get("/api/v1/deliveries")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
