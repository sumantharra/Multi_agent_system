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


def _create_delivery(
    client: TestClient,
    *,
    hostel_id: str,
    delivery_date: str,
    morning: str,
    evening: str,
    rate: str | None = None,
) -> None:
    payload: dict[str, str] = {
        "hostel_id": hostel_id,
        "delivery_date": delivery_date,
        "morning_quantity": morning,
        "evening_quantity": evening,
    }
    if rate is not None:
        payload["rate_per_liter"] = rate
    response = client.post("/api/v1/deliveries", json=payload)
    assert response.status_code == 201


def test_create_invoice_from_deliveries(client: TestClient) -> None:
    hostel_id = _create_hostel(client, code="sai-01", rate="45.50")
    _create_delivery(
        client,
        hostel_id=hostel_id,
        delivery_date="2026-07-01",
        morning="10",
        evening="0",
    )
    _create_delivery(
        client,
        hostel_id=hostel_id,
        delivery_date="2026-07-15",
        morning="5",
        evening="5",
        rate="50.00",
    )

    response = client.post(
        "/api/v1/invoices",
        json={
            "hostel_id": hostel_id,
            "billing_month": "2026-07",
            "tax": "10.00",
            "adjustments": "5.00",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["invoice_number"] == "INV-202607-SAI-01-001"
    assert body["billing_month"] == "2026-07"
    assert body["period_start"] == "2026-07-01"
    assert body["period_end"] == "2026-07-31"
    assert body["due_date"] == "2026-07-31"
    assert body["payment_status"] == "unpaid"
    assert Decimal(body["total_quantity"]) == Decimal("20.000")
    # 10L * 45.50 + 10L * 50.00 = 455.00 + 500.00
    assert Decimal(body["subtotal"]) == Decimal("955.00")
    assert Decimal(body["tax"]) == Decimal("10.00")
    assert Decimal(body["adjustments"]) == Decimal("5.00")
    assert Decimal(body["total_amount"]) == Decimal("970.00")
    assert len(body["items"]) == 2
    descriptions = {item["description"] for item in body["items"]}
    assert descriptions == {"Delivery 2026-07-01", "Delivery 2026-07-15"}

    fetched = client.get(f"/api/v1/invoices/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["invoice_number"] == "INV-202607-SAI-01-001"
    assert len(fetched.json()["items"]) == 2


def test_invoice_numbers_are_sequential_per_hostel(client: TestClient) -> None:
    sai = _create_hostel(client, code="sai-01")
    alpha = _create_hostel(client, code="alpha")
    _create_delivery(
        client, hostel_id=sai, delivery_date="2026-07-01", morning="1", evening="1"
    )
    _create_delivery(
        client, hostel_id=sai, delivery_date="2026-08-01", morning="1", evening="1"
    )
    _create_delivery(
        client, hostel_id=alpha, delivery_date="2026-07-01", morning="1", evening="1"
    )

    july_sai = client.post(
        "/api/v1/invoices",
        json={"hostel_id": sai, "billing_month": "2026-07"},
    )
    august_sai = client.post(
        "/api/v1/invoices",
        json={"hostel_id": sai, "billing_month": "2026-08"},
    )
    july_alpha = client.post(
        "/api/v1/invoices",
        json={"hostel_id": alpha, "billing_month": "2026-07"},
    )
    assert july_sai.status_code == 201
    assert august_sai.status_code == 201
    assert july_alpha.status_code == 201
    assert july_sai.json()["invoice_number"] == "INV-202607-SAI-01-001"
    assert august_sai.json()["invoice_number"] == "INV-202608-SAI-01-002"
    assert july_alpha.json()["invoice_number"] == "INV-202607-ALPHA-001"
    numbers = {
        july_sai.json()["invoice_number"],
        august_sai.json()["invoice_number"],
        july_alpha.json()["invoice_number"],
    }
    assert len(numbers) == 3


def test_duplicate_hostel_month_conflict(client: TestClient) -> None:
    hostel_id = _create_hostel(client)
    _create_delivery(
        client, hostel_id=hostel_id, delivery_date="2026-07-02", morning="2", evening="2"
    )
    payload = {"hostel_id": hostel_id, "billing_month": "2026-07"}
    assert client.post("/api/v1/invoices", json=payload).status_code == 201

    duplicate = client.post("/api/v1/invoices", json=payload)
    assert duplicate.status_code == 409
    body = duplicate.json()
    assert body["error"]["code"] == "CONFLICT"
    assert body["error"]["details"][0]["field"] == "billing_month"


def test_unknown_hostel_not_found(client: TestClient) -> None:
    response = client.post(
        "/api/v1/invoices",
        json={"hostel_id": str(uuid4()), "billing_month": "2026-07"},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_missing_invoice_not_found(client: TestClient) -> None:
    response = client.get(f"/api/v1/invoices/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_no_deliveries_for_month_is_validation_error(client: TestClient) -> None:
    hostel_id = _create_hostel(client)
    response = client.post(
        "/api/v1/invoices",
        json={"hostel_id": hostel_id, "billing_month": "2026-07"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_list_filters_by_hostel_month_and_status(client: TestClient) -> None:
    sai = _create_hostel(client, code="sai-01")
    alpha = _create_hostel(client, code="alpha")
    _create_delivery(
        client, hostel_id=sai, delivery_date="2026-07-01", morning="1", evening="0"
    )
    _create_delivery(
        client, hostel_id=sai, delivery_date="2026-08-01", morning="1", evening="0"
    )
    _create_delivery(
        client, hostel_id=alpha, delivery_date="2026-07-01", morning="1", evening="0"
    )
    assert (
        client.post(
            "/api/v1/invoices", json={"hostel_id": sai, "billing_month": "2026-07"}
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/invoices", json={"hostel_id": sai, "billing_month": "2026-08"}
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/invoices", json={"hostel_id": alpha, "billing_month": "2026-07"}
        ).status_code
        == 201
    )

    sai_july = client.get(
        "/api/v1/invoices",
        params={"hostel_id": sai, "billing_month": "2026-07", "payment_status": "unpaid"},
    )
    assert sai_july.status_code == 200
    listed = sai_july.json()
    assert listed["total"] == 1
    assert listed["items"][0]["hostel_id"] == sai
    assert listed["items"][0]["billing_month"] == "2026-07"
    assert listed["items"][0]["payment_status"] == "unpaid"


def test_invoices_require_auth_gate_when_disabled(client: TestClient) -> None:
    from app.core.config import Settings, get_settings
    from app.main import app as fastapi_app

    app_settings = Settings(
        app_env="development",
        allow_unauthenticated=False,
        database_url="sqlite:///:memory:",
    )

    fastapi_app.dependency_overrides[get_settings] = lambda: app_settings
    response = client.get("/api/v1/invoices")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
