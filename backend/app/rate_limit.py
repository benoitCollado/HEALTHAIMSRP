import os
import time
from dataclasses import dataclass

try:
    from redis import Redis
    from redis.exceptions import RedisError
except ModuleNotFoundError:  # pragma: no cover - exercised only when dependency is absent.
    Redis = None

    class RedisError(Exception):
        pass


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.middleware import _get_client_ip, _get_request_user_id
from app.observability.logger import get_logger

_log = get_logger("rate_limit")


def _flag_enabled(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int


class RedisRateLimiter:
    def __init__(self) -> None:
        self.redis_url = os.getenv("REDIS_URL", "").strip()
        self._client = None

    @property
    def enabled(self) -> bool:
        return _flag_enabled("RATE_LIMIT_ENABLED", True) and bool(os.getenv("REDIS_URL", self.redis_url).strip())

    def _redis(self) -> Redis:
        if Redis is None:
            raise RedisError("redis package is not installed")
        redis_url = os.getenv("REDIS_URL", self.redis_url).strip()
        if self._client is None or redis_url != self.redis_url:
            self.redis_url = redis_url
            self._client = Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
        return self._client

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitDecision:
        client = self._redis()
        redis_key = f"rate_limit:{key}:{int(time.time() // window_seconds)}"
        count = client.incr(redis_key)
        if count == 1:
            client.expire(redis_key, window_seconds)
        ttl = client.ttl(redis_key)
        reset = ttl if ttl and ttl > 0 else window_seconds
        remaining = max(0, limit - int(count))
        return RateLimitDecision(
            allowed=int(count) <= limit,
            limit=limit,
            remaining=remaining,
            reset_seconds=reset,
        )


rate_limiter = RedisRateLimiter()


def _route_limit(request: Request) -> tuple[int, int]:
    path = request.url.path
    if path.endswith("/login"):
        return _int_env("RATE_LIMIT_LOGIN_LIMIT", 10), _int_env("RATE_LIMIT_LOGIN_WINDOW_SECONDS", 60)
    if "/chat" in path:
        return _int_env("RATE_LIMIT_CHAT_LIMIT", 20), _int_env("RATE_LIMIT_CHAT_WINDOW_SECONDS", 60)
    return _int_env("RATE_LIMIT_DEFAULT_LIMIT", 120), _int_env("RATE_LIMIT_DEFAULT_WINDOW_SECONDS", 60)


def _actor_key(request: Request) -> str:
    user_id = _get_request_user_id(request)
    client_ip = _get_client_ip(request)
    if user_id is not None:
        return f"user:{user_id}:ip:{client_ip}"
    return f"ip:{client_ip}"


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not rate_limiter.enabled or request.url.path.endswith("/health"):
            return await call_next(request)

        limit, window_seconds = _route_limit(request)
        if limit <= 0 or window_seconds <= 0:
            return await call_next(request)

        key = f"{request.method}:{request.url.path}:{_actor_key(request)}"
        try:
            decision = rate_limiter.check(key, limit, window_seconds)
        except RedisError as exc:
            _log.warning("Redis rate limiting unavailable, request allowed: %s", exc)
            return await call_next(request)

        if not decision.allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Trop de requetes. Reessayez dans quelques instants."},
                headers={
                    "Retry-After": str(decision.reset_seconds),
                    "X-RateLimit-Limit": str(decision.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(decision.reset_seconds),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(decision.limit)
        response.headers["X-RateLimit-Remaining"] = str(decision.remaining)
        response.headers["X-RateLimit-Reset"] = str(decision.reset_seconds)
        return response
