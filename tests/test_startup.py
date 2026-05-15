from fastapi.testclient import TestClient

from src.main import app


def test_health_endpoint_returns_healthy() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "ai-search"}


def test_ready_endpoint_returns_ready() -> None:
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}