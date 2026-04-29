import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.observability.logger import get_logger
from app.observability.monitoring import metrics

_access_log = get_logger("access")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
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

        return response
