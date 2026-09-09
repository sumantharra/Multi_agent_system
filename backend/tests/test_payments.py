from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient


def _create_hostel(client: TestClient, *, code: str = "sai-01", rate: str = "45.50") -> str:
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


def _create_invoice(client: TestClient, *, due_date: str | None = "2026-12-31") -> tuple[str, str]:
    hostel_id = _create_hostel(client)
    delivery = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_id,
            "delivery_date": "2026-07-01",
            "morning_quantity": "10",
            "evening_quantity": "0",
        },
    )
    assert delivery.status_code == 201
    payload: dict[str, str] = {"hostel_id": hostel_id, "billing_month": "2026-07"}
    if due_date is not None:
        payload["due_date"] = due_date
    invoice = client.post("/api/v1/invoices", json=payload)
    assert invoice.status_code == 201
    return hostel_id, invoice.json()["id"]


def test_partial_then_paid_updates_invoice_status(client: TestClient) -> None:
    hostel_id, invoice_id = _create_invoice(client)
    invoice = client.get(f"/api/v1/invoices/{invoice_id}").json()
    total = Decimal(invoice["total_amount"])
    assert invoice["payment_status"] == "unpaid"

    partial = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice_id,
            "amount": "100.00",
            "payment_date": "2026-08-01",
            "payment_method": "upi",
            "reference_number": "UPI-1",
        },
    )
    assert partial.status_code == 201
    body = partial.json()
    assert body["hostel_id"] == hostel_id
    assert body["invoice_id"] == invoice_id
    assert Decimal(body["amount"]) == Decimal("100.00")
    assert body["payment_method"] == "upi"

    after_partial = client.get(f"/api/v1/invoices/{invoice_id}").json()
    assert after_partial["payment_status"] == "partial"

    remainder = total - Decimal("100.00")
    paid = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice_id,
            "amount": str(remainder),
            "payment_date": "2026-08-02",
            "payment_method": "cash",
        },
    )
    assert paid.status_code == 201
    after_paid = client.get(f"/api/v1/invoices/{invoice_id}").json()
    assert after_paid["payment_status"] == "paid"


def test_overpayment_marks_invoice_paid(client: TestClient) -> None:
    _, invoice_id = _create_invoice(client)
    total = Decimal(client.get(f"/api/v1/invoices/{invoice_id}").json()["total_amount"])
    response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice_id,
            "amount": str(total + Decimal("50.00")),
            "payment_date": "2026-08-03",
            "payment_method": "bank_transfer",
            "notes": "overpay",
        },
    )
    assert response.status_code == 201
    assert client.get(f"/api/v1/invoices/{invoice_id}").json()["payment_status"] == "paid"


def test_overdue_when_partial_and_due_date_passed(client: TestClient) -> None:
    _, invoice_id = _create_invoice(client, due_date="2020-01-15")
    response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice_id,
            "amount": "10.00",
            "payment_date": "2026-08-01",
            "payment_method": "cheque",
        },
    )
    assert response.status_code == 201
    assert client.get(f"/api/v1/invoices/{invoice_id}").json()["payment_status"] == "overdue"


def test_unknown_invoice_not_found(client: TestClient) -> None:
    response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": str(uuid4()),
            "amount": "10.00",
            "payment_date": "2026-08-01",
            "payment_method": "cash",
        },
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_missing_payment_not_found(client: TestClient) -> None:
    response = client.get(f"/api/v1/payments/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_list_filters_by_hostel_and_invoice(client: TestClient) -> None:
    hostel_a, invoice_a = _create_invoice(client)
    hostel_b = _create_hostel(client, code="alpha")
    delivery = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_b,
            "delivery_date": "2026-07-01",
            "morning_quantity": "2",
            "evening_quantity": "0",
        },
    )
    assert delivery.status_code == 201
    invoice_b = client.post(
        "/api/v1/invoices",
        json={"hostel_id": hostel_b, "billing_month": "2026-07", "due_date": "2026-12-31"},
    )
    assert invoice_b.status_code == 201
    invoice_b_id = invoice_b.json()["id"]

    assert (
        client.post(
            "/api/v1/payments",
            json={
                "invoice_id": invoice_a,
                "amount": "20.00",
                "payment_date": "2026-08-10",
                "payment_method": "cash",
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/payments",
            json={
                "invoice_id": invoice_b_id,
                "amount": "15.00",
                "payment_date": "2026-08-11",
                "payment_method": "upi",
            },
        ).status_code
        == 201
    )

    listed = client.get("/api/v1/payments", params={"hostel_id": hostel_a})
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] == 1
    assert body["items"][0]["hostel_id"] == hostel_a

    by_invoice = client.get("/api/v1/payments", params={"invoice_id": invoice_b_id})
    assert by_invoice.json()["total"] == 1
    assert by_invoice.json()["items"][0]["invoice_id"] == invoice_b_id

    fetched = client.get(f"/api/v1/payments/{body['items'][0]['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == body["items"][0]["id"]


def test_idempotency_key_replays_same_payment(client: TestClient) -> None:
    _, invoice_id = _create_invoice(client)
    payload = {
        "invoice_id": invoice_id,
        "amount": "25.00",
        "payment_date": "2026-08-12",
        "payment_method": "upi",
    }
    first = client.post(
        "/api/v1/payments",
        json=payload,
        headers={"Idempotency-Key": "pay-abc-1"},
    )
    second = client.post(
        "/api/v1/payments",
        json=payload,
        headers={"Idempotency-Key": "pay-abc-1"},
    )
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    listed = client.get("/api/v1/payments", params={"invoice_id": invoice_id})
    assert listed.json()["total"] == 1


def test_payments_require_auth_gate_when_disabled(client: TestClient) -> None:
    from app.core.config import Settings, get_settings
    from app.main import app as fastapi_app

    app_settings = Settings(
        app_env="development",
        allow_unauthenticated=False,
        database_url="sqlite:///:memory:",
    )

    fastapi_app.dependency_overrides[get_settings] = lambda: app_settings
    response = client.get("/api/v1/payments")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
