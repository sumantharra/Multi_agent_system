from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "multi-agent-api",
        "environment": "development",
    }


def test_health_check_allows_development_origin(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_unknown_route_returns_not_found(client: TestClient) -> None:
    response = client.get("/not-a-route")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_health_ready(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["service"] == "multi-agent-api"
    assert "request_id" in body
