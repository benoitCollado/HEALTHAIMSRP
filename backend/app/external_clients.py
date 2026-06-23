import os
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.cache import airflow_cache_ttl_seconds, airflow_stale_cache_ttl_seconds, cache
from app.observability.logger import get_logger

_log = get_logger("external_clients")

MISTRAL_CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
DEFAULT_MISTRAL_MODEL = "mistral-small-latest"
AIRFLOW_DAG_IDS = ["fetch_openfoodfacts_france", "export_db_to_csv", "incorporation_ml"]
AIRFLOW_CACHE_KEY = "external:airflow:dag_runs"


class ExternalServiceError(Exception):
    """Raised when an external provider cannot be used safely."""


class ExternalServiceAuthError(ExternalServiceError):
    """Raised when provider credentials are missing or rejected."""


class ExternalServiceResponseError(ExternalServiceError):
    """Raised when a provider returns an unusable payload."""


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int
    recovery_seconds: int
    failures: int = 0
    opened_at: float | None = None

    def allow_request(self) -> bool:
        if self.opened_at is None:
            return True
        if time.time() - self.opened_at >= self.recovery_seconds:
            self.failures = 0
            self.opened_at = None
            return True
        return False

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.opened_at = time.time()
            _log.warning("Circuit breaker opened for %s after %s failures", self.name, self.failures)


_breakers: dict[str, CircuitBreaker] = {}


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _get_breaker(name: str) -> CircuitBreaker:
    breaker = _breakers.get(name)
    if breaker is None:
        breaker = CircuitBreaker(
            name=name,
            failure_threshold=max(1, _int_env("EXTERNAL_API_CIRCUIT_FAILURES", 3)),
            recovery_seconds=max(1, _int_env("EXTERNAL_API_CIRCUIT_RECOVERY_SECONDS", 60)),
        )
        _breakers[name] = breaker
    return breaker


def _sleep_before_retry(attempt: int) -> None:
    base_delay = max(0.0, _float_env("EXTERNAL_API_RETRY_DELAY_SECONDS", 0.25))
    if base_delay:
        time.sleep(base_delay * (2**attempt))


def _request_with_resilience(
    service_name: str,
    method: str,
    url: str,
    *,
    timeout: float,
    retry_statuses: set[int] | None = None,
    **kwargs,
) -> httpx.Response:
    breaker = _get_breaker(service_name)
    if not breaker.allow_request():
        raise ExternalServiceError(f"{service_name} temporairement indisponible")

    retries = max(0, _int_env("EXTERNAL_API_MAX_RETRIES", 2))
    retry_statuses = retry_statuses or {429, 500, 502, 503, 504}
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.request(method, url, **kwargs)
            if response.status_code in retry_statuses:
                last_error = httpx.HTTPStatusError(
                    f"Retryable status code {response.status_code}",
                    request=response.request,
                    response=response,
                )
                if attempt < retries:
                    _sleep_before_retry(attempt)
                    continue
            response.raise_for_status()
            breaker.record_success()
            return response
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code not in retry_statuses or attempt >= retries:
                break
            _sleep_before_retry(attempt)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
            last_error = exc
            if attempt >= retries:
                break
            _sleep_before_retry(attempt)

    breaker.record_failure()
    if isinstance(last_error, httpx.HTTPStatusError) and last_error.response.status_code in (401, 403):
        raise ExternalServiceAuthError("Credentials refused by external provider") from last_error
    raise ExternalServiceError(f"{service_name} unavailable") from last_error


def get_mistral_api_key() -> str | None:
    return os.getenv("KEY_MISTRAL_API") or os.getenv("KEY_MISTRALL_API") or os.getenv("MISTRAL_API_KEY")


def build_chat_fallback_answer() -> str:
    return (
        "Le service IA est temporairement indisponible. Vous pouvez continuer a utiliser HealthAI MSPR "
        "pour consulter vos objectifs, consommations, activites et metriques. Pour une question de sante "
        "urgente ou des symptomes, contactez un professionnel de sante."
    )


def call_mistral_chat_completion(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | dict[str, Any] = "auto",
    max_tokens: int = 500,
) -> dict[str, Any]:
    api_key = get_mistral_api_key()
    if not api_key:
        raise ExternalServiceAuthError("API Mistral non configuree")

    payload: dict[str, Any] = {
        "model": os.getenv("MISTRAL_MODEL", DEFAULT_MISTRAL_MODEL),
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice

    response = _request_with_resilience(
        "mistral",
        "POST",
        MISTRAL_CHAT_URL,
        timeout=max(1.0, _float_env("MISTRAL_TIMEOUT_SECONDS", 20.0)),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    try:
        return response.json()["choices"][0]["message"]
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise ExternalServiceResponseError("Reponse Mistral invalide") from exc


def call_mistral_chat(messages: list[dict[str, str]]) -> str:
    message = call_mistral_chat_completion(messages)
    answer = (message.get("content") or "").strip()
    if not answer:
        raise ExternalServiceResponseError("Reponse Mistral vide")
    return answer


def _microservice_ia_base_url() -> str:
    return os.getenv("MICROSERVICE_IA_URL", "http://microservice_ia:8090").rstrip("/")


def _microservice_ia_timeout() -> float:
    return max(1.0, _float_env("MICROSERVICE_IA_TIMEOUT_SECONDS", 10.0))


def call_microservice_ia_calories(profile_payload: dict[str, Any]) -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "POST",
        f"{_microservice_ia_base_url()}/api/recommandation_calorique",
        timeout=_microservice_ia_timeout(),
        json=profile_payload,
    )
    try:
        return response.json()
    except ValueError as exc:
        raise ExternalServiceResponseError("Reponse microservice_ia invalide") from exc


def call_microservice_ia_exercises(profile_payload: dict[str, Any], *, limit: int = 5) -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "POST",
        f"{_microservice_ia_base_url()}/api/recommandation_exercice",
        timeout=_microservice_ia_timeout(),
        json={**profile_payload, "limit": limit},
    )
    try:
        return response.json()
    except ValueError as exc:
        raise ExternalServiceResponseError("Reponse microservice_ia invalide") from exc


def call_microservice_ia_recommendations(profile_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "calories": call_microservice_ia_calories(profile_payload),
        "exercices": call_microservice_ia_exercises(profile_payload, limit=5),
    }


def _microservice_ia_json_response(response: httpx.Response) -> dict[str, Any]:
    try:
        return response.json()
    except ValueError as exc:
        raise ExternalServiceResponseError("Reponse microservice_ia invalide") from exc


def call_microservice_ia_health() -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "GET",
        f"{_microservice_ia_base_url()}/health",
        timeout=_microservice_ia_timeout(),
    )
    return _microservice_ia_json_response(response)


def call_microservice_ia_generate_program(payload: dict[str, Any]) -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "POST",
        f"{_microservice_ia_base_url()}/api/v1/recommendations/generate",
        timeout=max(_microservice_ia_timeout(), 30.0),
        json=payload,
    )
    return _microservice_ia_json_response(response)


def call_microservice_ia_current_program(user_id: int) -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "GET",
        f"{_microservice_ia_base_url()}/api/v1/recommendations/current",
        timeout=_microservice_ia_timeout(),
        params={"user_id": user_id},
    )
    return _microservice_ia_json_response(response)


def call_microservice_ia_adjust_session(payload: dict[str, Any]) -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "POST",
        f"{_microservice_ia_base_url()}/api/v1/recommendations/adjust",
        timeout=_microservice_ia_timeout(),
        json=payload,
    )
    return _microservice_ia_json_response(response)


def call_microservice_ia_session_feedback(session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "POST",
        f"{_microservice_ia_base_url()}/api/v1/recommendations/sessions/{session_id}/feedback",
        timeout=_microservice_ia_timeout(),
        json=payload,
    )
    return _microservice_ia_json_response(response)


def call_microservice_ia_update_constraints(profile_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "PUT",
        f"{_microservice_ia_base_url()}/api/v1/profiles/{profile_id}/constraints",
        timeout=_microservice_ia_timeout(),
        json=payload,
    )
    return _microservice_ia_json_response(response)


def call_microservice_ia_profile_history(
    profile_id: int,
    *,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if date_from:
        params["date_from"] = date_from
    if date_to:
        params["date_to"] = date_to
    response = _request_with_resilience(
        "microservice_ia_recommendations",
        "GET",
        f"{_microservice_ia_base_url()}/api/v1/profiles/{profile_id}/history",
        timeout=_microservice_ia_timeout(),
        params=params or None,
    )
    return _microservice_ia_json_response(response)


def call_photo_processing(image_payload: dict[str, Any]) -> dict[str, Any]:
    url = os.getenv("PHOTO_PROCESSING_API_URL", "http://microservice_photo:8000/analyze")

    response = _request_with_resilience(
        "photo_processing",
        "POST",
        url,
        timeout=max(1.0, _float_env("PHOTO_PROCESSING_TIMEOUT_SECONDS", 20.0)),
        json=image_payload,
    )

    try:
        return response.json()
    except ValueError as exc:
        raise ExternalServiceResponseError("Reponse traitement photo invalide") from exc


def fetch_airflow_dag_runs() -> tuple[dict[str, Any], str]:
    cached = cache.get_json(AIRFLOW_CACHE_KEY)
    if cached is not None:
        return cached, "cached"

    base_url = os.getenv("AIRFLOW_API_URL", "http://airflow-webserver:8080").rstrip("/")
    user = os.getenv("AIRFLOW_USER", "airflow")
    password = os.getenv("AIRFLOW_PASSWORD", "airflow")
    auth = (user, password) if user and password else None
    result: dict[str, Any] = {}

    try:
        response = _request_with_resilience(
            "airflow",
            "GET",
            f"{base_url}/api/v1/dags",
            timeout=max(1.0, _float_env("AIRFLOW_API_TIMEOUT_SECONDS", 10.0)),
            auth=auth,
        )
        dags_data = response.json()
        all_dag_ids = [d["dag_id"] for d in dags_data.get("dags", [])]
        dag_ids = [dag_id for dag_id in AIRFLOW_DAG_IDS if dag_id in all_dag_ids] or AIRFLOW_DAG_IDS

        for dag_id in dag_ids:
            try:
                runs_response = _request_with_resilience(
                    "airflow",
                    "GET",
                    f"{base_url}/api/v1/dags/{dag_id}/dagRuns",
                    timeout=max(1.0, _float_env("AIRFLOW_API_TIMEOUT_SECONDS", 10.0)),
                    params={"limit": 10},
                    auth=auth,
                )
                runs = runs_response.json().get("dag_runs", [])
                result[dag_id] = {"runs": runs, "last_run": runs[0] if runs else None}
            except ExternalServiceError as exc:
                _log.warning("Airflow DAG run fetch failed for %s: %s", dag_id, exc)
                result[dag_id] = {"runs": [], "last_run": None}
    except (ExternalServiceError, ValueError, KeyError) as exc:
        _log.warning("Airflow unavailable, using degraded flux fallback: %s", exc)
        cached_fallback = cache.get_fresh_or_stale(AIRFLOW_CACHE_KEY)
        if cached_fallback is not None:
            return cached_fallback.data, cached_fallback.state
        return {}, "degraded"

    cache.set_fresh_and_stale(
        AIRFLOW_CACHE_KEY,
        result,
        airflow_cache_ttl_seconds(),
        airflow_stale_cache_ttl_seconds(),
    )
    return result, "ok"
