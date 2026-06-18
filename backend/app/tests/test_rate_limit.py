from unittest.mock import patch

from app.rate_limit import RateLimitDecision, RedisError


def test_rate_limit_blocks_after_redis_decision(client, monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")

    decision = RateLimitDecision(allowed=False, limit=1, remaining=0, reset_seconds=30)
    with patch("app.rate_limit.rate_limiter.check", return_value=decision):
        response = client.get("/aliments/")

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "30"
    assert response.json()["detail"] == "Trop de requetes. Reessayez dans quelques instants."


def test_rate_limit_fail_open_when_redis_is_unavailable(client, admin_headers, monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")

    with patch("app.rate_limit.rate_limiter.check", side_effect=RedisError("down")):
        response = client.get("/aliments/", headers=admin_headers)

    assert response.status_code == 200
