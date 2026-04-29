import pytest
import email as email_lib
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, call

import app.observability.email_alert as email_alert_module
from app.observability.email_alert import (
    send_error_alert,
    _is_on_cooldown,
    _get_stacktrace,
    _COOLDOWN_SECONDS,
)

ENV_VARS = {
    "EMAIL_USER": "sender@gmail.com",
    "EMAIL_PASS": "app_password",
    "ADMIN_EMAIL": "admin@example.com",
}


# ──────────────────────────────────────────────
# _is_on_cooldown
# ──────────────────────────────────────────────

def test_cooldown_false_when_no_entry():
    email_alert_module._last_sent.clear()
    assert _is_on_cooldown("SomeError:/api/test") is False


def test_cooldown_true_within_window():
    email_alert_module._last_sent.clear()
    key = "SomeError:/api/test"
    email_alert_module._last_sent[key] = datetime.utcnow()
    assert _is_on_cooldown(key) is True


def test_cooldown_false_after_window():
    email_alert_module._last_sent.clear()
    key = "SomeError:/api/test"
    email_alert_module._last_sent[key] = datetime.utcnow() - timedelta(seconds=_COOLDOWN_SECONDS + 1)
    assert _is_on_cooldown(key) is False


# ──────────────────────────────────────────────
# _get_stacktrace
# ──────────────────────────────────────────────

def test_get_stacktrace_no_real_traceback():
    error = ValueError("simple error")
    result = _get_stacktrace(error)
    assert "simple error" in result


def test_get_stacktrace_with_real_traceback():
    try:
        raise RuntimeError("boom")
    except RuntimeError as e:
        result = _get_stacktrace(e)
    assert "RuntimeError" in result
    assert "boom" in result


# ──────────────────────────────────────────────
# send_error_alert — env not configured
# ──────────────────────────────────────────────

def test_send_no_smtp_config_skips(capsys):
    email_alert_module._last_sent.clear()
    with patch.dict("os.environ", {}, clear=True):
        send_error_alert(ValueError("test"))
    captured = capsys.readouterr()
    assert "SMTP non configuré" in captured.out


def test_send_partial_config_skips(capsys):
    email_alert_module._last_sent.clear()
    with patch.dict("os.environ", {"EMAIL_PASS": "x"}, clear=True):
        send_error_alert(ValueError("test"))
    captured = capsys.readouterr()
    assert "SMTP non configuré" in captured.out


# ──────────────────────────────────────────────
# send_error_alert — cooldown blocks send
# ──────────────────────────────────────────────

def test_send_blocked_by_cooldown():
    email_alert_module._last_sent.clear()
    error = KeyError("rate-limit-test")
    key = f"{type(error).__name__}:/api/route"
    email_alert_module._last_sent[key] = datetime.utcnow()

    with patch.dict("os.environ", ENV_VARS):
        with patch("smtplib.SMTP") as mock_smtp:
            send_error_alert(error, url="/api/route")
            mock_smtp.assert_not_called()


# ──────────────────────────────────────────────
# send_error_alert — successful send
# ──────────────────────────────────────────────

def test_send_calls_smtp_correctly(capsys):
    email_alert_module._last_sent.clear()

    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    with patch.dict("os.environ", ENV_VARS):
        with patch("smtplib.SMTP", mock_smtp_cls):
            send_error_alert(ValueError("db error"), method="GET", url="/api/aliments", user_id=42)

    mock_smtp_cls.assert_called_once_with("smtp.gmail.com", 587, timeout=10)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("sender@gmail.com", "app_password")
    mock_server.sendmail.assert_called_once()

    args = mock_server.sendmail.call_args[0]
    assert args[0] == "sender@gmail.com"
    assert args[1] == "admin@example.com"
    assert "[ALERTE]" in args[2]

    captured = capsys.readouterr()
    assert "Email envoyé" in captured.out


def test_send_email_contains_error_details(capsys):
    email_alert_module._last_sent.clear()

    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    with patch.dict("os.environ", ENV_VARS):
        with patch("smtplib.SMTP", mock_smtp_cls):
            send_error_alert(TypeError("bad type"), method="POST", url="/api/login")

    raw_email = mock_server.sendmail.call_args[0][2]
    # Subject and headers are not encoded
    assert "TypeError" in raw_email
    assert "/api/login" in raw_email

    # Body parts are base64-encoded — decode each MIME part to check content
    msg = email_lib.message_from_string(raw_email)
    body_text = ""
    for part in msg.walk():
        payload = part.get_payload(decode=True)
        if payload:
            body_text += payload.decode("utf-8", errors="replace")

    assert "bad type" in body_text
    assert "POST" in body_text


def test_send_records_cooldown_timestamp():
    email_alert_module._last_sent.clear()

    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    error = OSError("disk full")
    key = f"{type(error).__name__}:/api/data"

    with patch.dict("os.environ", ENV_VARS):
        with patch("smtplib.SMTP", mock_smtp_cls):
            send_error_alert(error, url="/api/data")

    assert key in email_alert_module._last_sent
    assert isinstance(email_alert_module._last_sent[key], datetime)


# ──────────────────────────────────────────────
# send_error_alert — SMTP failure
# ──────────────────────────────────────────────

def test_send_smtp_exception_does_not_raise(capsys):
    email_alert_module._last_sent.clear()

    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(side_effect=Exception("connection refused"))
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    with patch.dict("os.environ", ENV_VARS):
        with patch("smtplib.SMTP", mock_smtp_cls):
            send_error_alert(ValueError("trigger"), url="/api/fail")

    captured = capsys.readouterr()
    assert "Erreur envoi mail" in captured.out


# ──────────────────────────────────────────────
# send_error_alert — EMAIL_USER fallback
# ──────────────────────────────────────────────

def test_send_uses_admin_email_as_fallback_sender(capsys):
    email_alert_module._last_sent.clear()
    env_no_user = {"EMAIL_PASS": "app_password", "ADMIN_EMAIL": "admin@example.com"}

    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    with patch.dict("os.environ", env_no_user, clear=True):
        with patch("smtplib.SMTP", mock_smtp_cls):
            send_error_alert(ValueError("fallback test"), url="/api/x")

    mock_server.login.assert_called_once_with("admin@example.com", "app_password")
