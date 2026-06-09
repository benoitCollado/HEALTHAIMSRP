import logging
import os
import time

from app.observability.email_alert import send_error_alert
from app.observability.logger import get_logger
from app.observability.monitoring import metrics
from app.security import verify_token
from starlette.background import BackgroundTask, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_access_log = get_logger("access")
_forbidden_attempts: dict[str, list[float]] = {}
_last_forbidden_alert: dict[str, float] = {}


class HttpStatusAlertError(Exception):
    """Synthetic error used for handled 5xx responses."""


class ForbiddenAccessAlertError(Exception):
    """Synthetic error used for HTTP 403 security alerts."""


def _flag_enabled(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _email_alerts_enabled() -> bool:
    app_env = os.getenv("APP_ENV", "").strip().lower()
    if app_env in {"test", "testing"} and not _flag_enabled("ERROR_ALERT_EMAILS_IN_TESTS", False):
        return False
    return _flag_enabled("ERROR_ALERT_EMAIL_ENABLED", True)


def _forbidden_alerts_enabled() -> bool:
    return _flag_enabled("ERROR_ALERT_ON_403", True)


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _get_request_user_id(request: Request):
    auth = request.headers.get("authorization", "")
    scheme, _, token = auth.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    sub = payload.get("sub")
    try:
        return int(sub)
    except (TypeError, ValueError):
        return sub


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",", 1)[0].strip()
    if not client_ip and request.client:
        client_ip = request.client.host
    return client_ip or "unknown"


def _format_request_user(user_id) -> str:
    return str(user_id) if user_id is not None else "anonymous"


def _get_request_actor_key(request: Request, user_id) -> str:
    client_ip = _get_client_ip(request)
    return f"user:{user_id}|ip:{client_ip}" if user_id is not None else f"ip:{client_ip}"


def _format_route_with_query(request: Request) -> str:
    route = request.url.path
    if request.url.query:
        return f"{route}?{request.url.query}"
    return route


def _log_request(request: Request, status: int, duration_ms: float, user_id) -> None:
    route = _format_route_with_query(request)
    client_ip = _get_client_ip(request)
    user = _format_request_user(user_id)
    category = "client_error" if 400 <= status < 500 else "server_error" if status >= 500 else "ok"
    level = logging.WARNING if status >= 400 else logging.INFO

    _access_log.log(
        level,
        "%s %s -> %d category=%s user=%s ip=%s duration_ms=%.1f",
        request.method,
        route,
        status,
        category,
        user,
        client_ip,
        duration_ms,
    )


def _should_alert_forbidden_burst(request: Request, user_id) -> tuple[bool, int, int]:
    if not _forbidden_alerts_enabled():
        return False, 0, 0

    threshold = max(1, _int_env("ERROR_ALERT_403_THRESHOLD", 5))
    window_seconds = max(1, _int_env("ERROR_ALERT_403_WINDOW_SECONDS", 300))
    cooldown_seconds = max(1, _int_env("ERROR_ALERT_403_COOLDOWN_SECONDS", 300))

    now = time.time()
    actor_key = _get_request_actor_key(request, user_id)
    cutoff = now - window_seconds
    attempts = [timestamp for timestamp in _forbidden_attempts.get(actor_key, []) if timestamp >= cutoff]
    attempts.append(now)
    _forbidden_attempts[actor_key] = attempts

    count = len(attempts)
    last_alert = _last_forbidden_alert.get(actor_key, 0)
    if count < threshold or now - last_alert < cooldown_seconds:
        return False, count, window_seconds

    _last_forbidden_alert[actor_key] = now
    return True, count, window_seconds


def _attach_error_alert(request: Request, response, user_id=None):
    if not _email_alerts_enabled():
        return

    if user_id is None:
        user_id = _get_request_user_id(request)

    if response.status_code == 403:
        should_alert, count, window_seconds = _should_alert_forbidden_burst(request, user_id)
        if not should_alert:
            return
        error = ForbiddenAccessAlertError(
            "ALERTE SECURITE: rafale de refus HTTP 403 detectee. "
            f"{count} refus sur {window_seconds} secondes pour le meme client/utilisateur. "
            "Cela peut indiquer une tentative d'acces non autorisee."
        )
    elif response.status_code >= 500 and not getattr(request.state, "error_alert_scheduled", False):
        error = HttpStatusAlertError(f"HTTP {response.status_code} response")
    else:
        return

    alert_task = BackgroundTask(
        send_error_alert,
        error,
        request.method,
        str(request.url),
        user_id,
    )

    if response.background is None:
        response.background = alert_task
        return

    background_tasks = BackgroundTasks([response.background])
    background_tasks.add_task(alert_task)
    response.background = background_tasks


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: fastapi.tiangolo.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        route = request.url.path
        status = response.status_code
        user_id = _get_request_user_id(request)
        metrics.record(route, duration_ms, status)
        _log_request(request, status, duration_ms, user_id)

        _attach_error_alert(request, response, user_id)

        return response
