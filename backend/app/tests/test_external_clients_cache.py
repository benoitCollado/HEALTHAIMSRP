from unittest.mock import MagicMock, patch

from app.external_clients import AIRFLOW_CACHE_KEY, ExternalServiceError, fetch_airflow_dag_runs


def test_fetch_airflow_dag_runs_returns_fresh_cache_without_http_call():
    cached = {"fetch_openfoodfacts_france": {"runs": [], "last_run": None}}

    with (
        patch("app.external_clients.cache.get_json", return_value=cached),
        patch("app.external_clients._request_with_resilience") as request,
    ):
        data, status = fetch_airflow_dag_runs()

    assert data == cached
    assert status == "cached"
    request.assert_not_called()


def test_fetch_airflow_dag_runs_uses_stale_cache_when_airflow_is_down():
    stale = MagicMock()
    stale.data = {"export_db_to_csv": {"runs": [], "last_run": None}}
    stale.state = "stale"

    with (
        patch("app.external_clients.cache.get_json", return_value=None),
        patch("app.external_clients.cache.get_fresh_or_stale", return_value=stale),
        patch("app.external_clients._request_with_resilience", side_effect=ExternalServiceError("down")),
    ):
        data, status = fetch_airflow_dag_runs()

    assert data == stale.data
    assert status == "stale"


def test_fetch_airflow_dag_runs_writes_fresh_and_stale_cache(monkeypatch):
    monkeypatch.setenv("EXTERNAL_API_MAX_RETRIES", "0")

    dags_response = MagicMock()
    dags_response.json.return_value = {"dags": [{"dag_id": "fetch_openfoodfacts_france"}]}

    runs_response = MagicMock()
    runs_response.json.return_value = {"dag_runs": [{"run_id": "scheduled__2026-06-18", "state": "success"}]}

    with (
        patch("app.external_clients.cache.get_json", return_value=None),
        patch("app.external_clients._request_with_resilience", side_effect=[dags_response, runs_response]),
        patch("app.external_clients.cache.set_fresh_and_stale") as set_cache,
    ):
        data, status = fetch_airflow_dag_runs()

    assert status == "ok"
    assert data["fetch_openfoodfacts_france"]["last_run"]["state"] == "success"
    set_cache.assert_called_once()
    assert set_cache.call_args.args[0] == AIRFLOW_CACHE_KEY
