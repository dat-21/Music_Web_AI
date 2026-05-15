from __future__ import annotations

import logging
import re

from fastapi.testclient import TestClient
from src.main import app


def test_request_id_propagation() -> None:
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-ID": "test-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-123"


def test_auto_generated_request_id() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    request_id_value = response.headers["X-Request-ID"]
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        request_id_value,
        re.IGNORECASE,
    )


def test_standardized_error_response() -> None:
    with TestClient(app) as client:
        response = client.get("/error")

    assert response.status_code == 400
    body = response.json()
    assert body["status"] == "error"
    assert body["error"]["message"] == "Invalid request"
    assert body["error"]["code"] == 400
    assert body["error"]["error_code"] == "invalid_request"


def test_cors_headers() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_logging_includes_request_id(caplog) -> None:
    caplog.set_level(logging.INFO)
    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-ID": "test-123"})

    assert response.status_code == 200
    log_entries = [record for record in caplog.records if record.message == "request_completed"]
    assert log_entries
    assert any(getattr(record, "request_id", None) == "test-123" for record in log_entries)