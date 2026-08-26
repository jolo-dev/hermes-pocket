from __future__ import annotations

import logging

from _pytest.logging import LogCaptureFixture
from fastapi.testclient import TestClient

from hermes_pocket.app import create_app


def test_health_returns_correlation_id() -> None:
    client = TestClient(create_app(configure_service_logging=False))

    response = client.get("/health", headers={"x-request-id": "request-health-1"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "request-health-1"
    assert response.json() == {"status": "ok", "correlation_id": "request-health-1"}


def test_invalid_request_id_is_replaced() -> None:
    client = TestClient(create_app(configure_service_logging=False))

    response = client.get("/health", headers={"x-request-id": "unsafe request id"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] != "unsafe request id"
    assert len(response.headers["x-request-id"]) == 32


def test_errors_are_structured_and_content_free(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="hermes_pocket.requests")
    client = TestClient(create_app(configure_service_logging=False))
    private_marker = "do-not-log-this-query-value"

    response = client.get(f"/missing?private={private_marker}", headers={"x-request-id": "error-1"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "HTTP_404",
            "category": "validation",
            "message": "The request was rejected.",
            "correlation_id": "error-1",
            "retryable": False,
        }
    }
    service_logs = " ".join(
        record.getMessage() for record in caplog.records if record.name == "hermes_pocket.requests"
    )
    assert private_marker not in service_logs
    assert "request_complete" in service_logs


def test_safe_log_fields_reject_content_keys() -> None:
    from hermes_pocket.logging import safe_log_fields

    try:
        safe_log_fields(request_id="request-1", event="unsafe", text="private")
    except ValueError as exception:
        assert str(exception) == "Content-bearing fields are prohibited in service diagnostics"
    else:
        raise AssertionError("safe_log_fields accepted a content-bearing field")
