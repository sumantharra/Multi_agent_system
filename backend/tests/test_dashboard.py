from datetime import date
from decimal import Decimal

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


def _create_delivery(
    client: TestClient,
    hostel_id: str,
    *,
    delivery_date: str,
    morning: str = "10",
    evening: str = "5",
) -> None:
    response = client.post(
        "/api/v1/deliveries",
        json={
            "hostel_id": hostel_id,
            "delivery_date": delivery_date,
            "morning_quantity": morning,
            "evening_quantity": evening,
        },
    )
    assert response.status_code == 201


def _create_invoice(client: TestClient, hostel_id: str, billing_month: str) -> dict:
    response = client.post(
        "/api/v1/invoices",
        json={"hostel_id": hostel_id, "billing_month": billing_month, "due_date": "2026-12-31"},
    )
    assert response.status_code == 201
    return response.json()


def test_empty_database_returns_zero_kpis(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["active_hostel_count"] == 0
    assert Decimal(body["todays_supply"]) == Decimal("0.000")
    assert Decimal(body["revenue"]) == Decimal("0.00")
    assert Decimal(body["pending_payments"]) == Decimal("0.00")
    assert body["timezone"] == "Asia/Kolkata"
    assert "paid" in body["revenue_definition"]
    assert "unpaid" in body["pending_definition"]


def test_dashboard_aggregates_match_seeded_rows(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.services.dashboard.business_today",
        lambda _timezone: date(2026, 9, 10),
    )

    active = _create_hostel(client, code="sai-01")
    inactive = _create_hostel(client, code="old-01")
    assert client.delete(f"/api/v1/hostels/{inactive}").status_code == 200

    _create_delivery(client, active, delivery_date="2026-09-10", morning="12", evening="8")
    _create_delivery(client, active, delivery_date="2026-09-09", morning="100", evening="0")

    current = _create_invoice(client, active, "2026-09")
    previous_hostel = _create_hostel(client, code="alpha-01")
    _create_delivery(client, previous_hostel, delivery_date="2026-08-01", morning="4", evening="0")
    previous = _create_invoice(client, previous_hostel, "2026-08")

    assert (
        client.post(
            "/api/v1/payments",
            json={
                "invoice_id": current["id"],
                "amount": current["total_amount"],
                "payment_date": "2026-09-10",
                "payment_method": "upi",
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/v1/payments",
            json={
                "invoice_id": previous["id"],
                "amount": previous["total_amount"],
                "payment_date": "2026-08-15",
                "payment_method": "cash",
            },
        ).status_code
        == 201
    )

    unpaid_hostel = _create_hostel(client, code="beta-01")
    _create_delivery(client, unpaid_hostel, delivery_date="2026-09-02", morning="2", evening="0")
    unpaid = _create_invoice(client, unpaid_hostel, "2026-09")
    partial_amount = (Decimal(unpaid["total_amount"]) / 2).quantize(Decimal("0.01"))
    assert (
        client.post(
            "/api/v1/payments",
            json={
                "invoice_id": unpaid["id"],
                "amount": str(partial_amount),
                "payment_date": "2026-09-10",
                "payment_method": "upi",
            },
        ).status_code
        == 201
    )

    body = client.get("/api/v1/dashboard").json()
    assert body["as_of_date"] == "2026-09-10"
    assert body["revenue_month"] == "2026-09"
    assert body["active_hostel_count"] == 3
    assert Decimal(body["todays_supply"]) == Decimal("20.000")
    assert Decimal(body["revenue"]) == Decimal(current["total_amount"])
    remaining = Decimal(unpaid["total_amount"]) - partial_amount
    assert Decimal(body["pending_payments"]) == remaining


def test_todays_supply_uses_business_date_not_utc(client: TestClient, monkeypatch) -> None:
    hostel_id = _create_hostel(client, code="tz-01")
    _create_delivery(client, hostel_id, delivery_date="2026-09-10", morning="3", evening="1")
    _create_delivery(client, hostel_id, delivery_date="2026-09-09", morning="50", evening="0")

    monkeypatch.setattr(
        "app.services.dashboard.business_today",
        lambda _timezone: date(2026, 9, 10),
    )
    after_midnight = client.get("/api/v1/dashboard").json()
    assert after_midnight["as_of_date"] == "2026-09-10"
    assert Decimal(after_midnight["todays_supply"]) == Decimal("4.000")

    monkeypatch.setattr(
        "app.services.dashboard.business_today",
        lambda _timezone: date(2026, 9, 9),
    )
    before_midnight = client.get("/api/v1/dashboard").json()
    assert before_midnight["as_of_date"] == "2026-09-09"
    assert Decimal(before_midnight["todays_supply"]) == Decimal("50.000")
