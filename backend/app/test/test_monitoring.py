import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError

import app.observability.monitoring as monitoring_module
from app.observability.monitoring import metrics


@pytest.fixture(autouse=True)
def reset_metrics():
    metrics.reset()
    yield
    metrics.reset()


# ──────────────────────────────────────────────
# /health
# ──────────────────────────────────────────────

def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_health_db_error(client):
    with patch("app.main.engine") as mock_engine:
        mock_engine.connect.side_effect = OperationalError("conn", {}, Exception("timeout"))
        response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "error"


def test_health_has_security_headers(client):
    response = client.get("/health")
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("x-content-type-options") == "nosniff"


# ──────────────────────────────────────────────
# /metrics
# ──────────────────────────────────────────────

def test_metrics_initial_state(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert "uptime_seconds" in body
    assert "requests_total" in body
    assert "errors_total" in body
    assert "avg_duration_ms" in body
    assert "requests_by_route" in body


def test_metrics_counts_requests(client, admin_headers):
    client.get("/aliments", headers=admin_headers)
    client.get("/aliments", headers=admin_headers)
    client.get("/aliments", headers=admin_headers)

    response = client.get("/metrics")
    body = response.json()
    assert body["requests_total"] >= 3
    assert "/aliments" in body["requests_by_route"]
    assert body["requests_by_route"]["/aliments"] >= 3


def test_metrics_counts_errors(client):
    client.get("/utilisateurs")  # 401 — not authenticated

    response = client.get("/metrics")
    body = response.json()
    assert body["errors_total"] == 0  # 401 is not a 5xx


def test_metrics_avg_duration_positive(client, admin_headers):
    client.get("/exercices", headers=admin_headers)
    response = client.get("/metrics")
    body = response.json()
    assert body["avg_duration_ms"] >= 0


def test_metrics_uptime_non_negative(client):
    response = client.get("/metrics")
    body = response.json()
    assert body["uptime_seconds"] >= 0


# ──────────────────────────────────────────────
# _Metrics unit tests
# ──────────────────────────────────────────────

def test_metrics_record_increments_total():
    metrics.record("/api/test", 50.0, 200)
    snap = metrics.snapshot()
    assert snap["requests_total"] == 1
    assert snap["errors_total"] == 0


def test_metrics_record_500_increments_errors():
    metrics.record("/api/broken", 10.0, 500)
    snap = metrics.snapshot()
    assert snap["errors_total"] == 1


def test_metrics_record_4xx_not_error():
    metrics.record("/api/missing", 5.0, 404)
    snap = metrics.snapshot()
    assert snap["errors_total"] == 0


def test_metrics_avg_duration():
    metrics.record("/a", 100.0, 200)
    metrics.record("/b", 200.0, 200)
    snap = metrics.snapshot()
    assert snap["avg_duration_ms"] == 150.0


def test_metrics_reset_clears_all():
    metrics.record("/x", 99.0, 200)
    metrics.reset()
    snap = metrics.snapshot()
    assert snap["requests_total"] == 0
    assert snap["errors_total"] == 0
    assert snap["avg_duration_ms"] == 0.0
    assert snap["requests_by_route"] == {}
