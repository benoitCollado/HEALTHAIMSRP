import json
import os
from hashlib import sha256
from dataclasses import dataclass
from typing import Any

try:
    from redis import Redis
    from redis.exceptions import RedisError
except ModuleNotFoundError:  # pragma: no cover - exercised only when dependency is absent.
    Redis = None

    class RedisError(Exception):
        pass


from app.observability.logger import get_logger

_log = get_logger("cache")


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
class CacheValue:
    data: Any
    state: str


class RedisJsonCache:
    def __init__(self) -> None:
        self.redis_url = os.getenv("REDIS_URL", "").strip()
        self._client = None

    @property
    def enabled(self) -> bool:
        redis_url = os.getenv("REDIS_URL", self.redis_url).strip()
        return _flag_enabled("CACHE_ENABLED", True) and bool(redis_url)

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

    def get_json(self, key: str) -> Any | None:
        if not self.enabled:
            return None
        try:
            value = self._redis().get(key)
        except RedisError as exc:
            _log.warning("Redis cache read failed for %s: %s", key, exc)
            return None
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            _log.warning("Redis cache entry is invalid JSON: %s", key)
            return None

    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        if not self.enabled or ttl_seconds <= 0:
            return
        try:
            self._redis().setex(key, ttl_seconds, json.dumps(value, default=str))
        except (TypeError, RedisError) as exc:
            _log.warning("Redis cache write failed for %s: %s", key, exc)

    def get_fresh_or_stale(self, key: str) -> CacheValue | None:
        fresh = self.get_json(key)
        if fresh is not None:
            return CacheValue(data=fresh, state="cached")

        stale = self.get_json(f"{key}:stale")
        if stale is not None:
            return CacheValue(data=stale, state="stale")
        return None

    def set_fresh_and_stale(self, key: str, value: Any, ttl_seconds: int, stale_ttl_seconds: int) -> None:
        self.set_json(key, value, ttl_seconds)
        self.set_json(f"{key}:stale", value, stale_ttl_seconds)


cache = RedisJsonCache()


def airflow_cache_ttl_seconds() -> int:
    return max(0, _int_env("AIRFLOW_CACHE_TTL_SECONDS", 60))


def airflow_stale_cache_ttl_seconds() -> int:
    return max(0, _int_env("AIRFLOW_STALE_CACHE_TTL_SECONDS", 900))


def chat_cache_ttl_seconds() -> int:
    return min(180, max(0, _int_env("CHAT_CACHE_TTL_SECONDS", 120)))


def minio_image_cache_ttl_seconds() -> int:
    return min(180, max(0, _int_env("MINIO_IMAGE_CACHE_TTL_SECONDS", 180)))


def stable_cache_key(prefix: str, value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    digest = sha256(payload.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"
