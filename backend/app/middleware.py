import logging
import time

from app.observability.email_alert import send_error_alert
from app.observability.logger import get_logger
from app.observability.monitoring import metrics
from app.security import verify_token
from starlette.background import BackgroundTask, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_access_log = get_logger("access")


class HttpStatusAlertError(Exception):
    """Synthetic error used for handled 5xx responses."""


class ForbiddenAccessAlertError(Exception):
    """Synthetic error used for HTTP 403 security alerts."""


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


def _attach_error_alert(request: Request, response):
    if response.status_code == 403:
        error = ForbiddenAccessAlertError(
            "ALERTE SECURITE: acces interdit HTTP 403. Cela peut indiquer une tentative d'acces non autorisee."
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
        _get_request_user_id(request),
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
        metrics.record(route, duration_ms, status)

        level = logging.WARNING if status >= 400 else logging.INFO
        _access_log.log(
            level,
            "%s %s → %d (%.1f ms)",
            request.method,
            route,
            status,
            duration_ms,
        )

        _attach_error_alert(request, response)

        return response
