import os
import smtplib
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.observability.logger import get_logger

# ==============================
# CONFIG
# ==============================

_last_sent: dict[str, datetime] = {}
_COOLDOWN_SECONDS = 60
_log = get_logger("email_alert")


# ==============================
# UTILS
# ==============================


def _is_on_cooldown(error_key: str) -> bool:
    """Avoid flooding the admin with repeated alerts for the same route/error."""
    last = _last_sent.get(error_key)
    if last is None:
        return False
    return (datetime.utcnow() - last).total_seconds() < _COOLDOWN_SECONDS


def _get_stacktrace(error: Exception) -> str:
    """Return the active traceback, or the error message when called outside except."""
    tb = traceback.format_exc()
    if tb.strip() == "NoneType: None":
        return str(error)
    return tb


# ==============================
# MAIN FUNCTION
# ==============================


def send_error_alert(
    error: Exception,
    method: str = "",
    url: str = "",
    user_id: int | None = None,
) -> None:
    """
    Envoie un email d'alerte en cas d'erreur backend.
    """

    # === ENV ===
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    admin_email = os.getenv("ADMIN_EMAIL")
    smtp_user = os.getenv("SMTP_USER") or os.getenv("EMAIL_USER") or admin_email
    smtp_password = os.getenv("SMTP_PASS") or os.getenv("EMAIL_PASS")

    missing = []
    if not smtp_user:
        missing.append("SMTP_USER")
    if not smtp_password:
        missing.append("SMTP_PASS")
    if not admin_email:
        missing.append("ADMIN_EMAIL")
    if missing:
        message = f"SMTP non configure - variables manquantes: {', '.join(missing)}"
        _log.warning("[ERROR ALERT] %s", message)
        print(f"[ERROR ALERT] {message}")
        return

    # Group alerts by exception type and URL so one noisy endpoint cannot flood
    # the mailbox while unrelated errors still produce their own alert.
    error_key = f"{type(error).__name__}:{url}"
    if _is_on_cooldown(error_key):
        _log.info("[ERROR ALERT] Alerte ignoree par cooldown: %s", error_key)
        return
    _last_sent[error_key] = datetime.utcnow()

    # === DATA ===
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    tb = _get_stacktrace(error)
    is_security_alert = type(error).__name__ == "ForbiddenAccessAlertError"
    alert_title = "Alerte securite HTTP 403" if is_security_alert else "Erreur API"
    alert_intro = (
        "Acces interdit detecte. Verifiez si cette requete correspond a une tentative "
        "d'intrusion, un token vole, ou un utilisateur sans droits admin."
        if is_security_alert
        else "Erreur backend detectee."
    )
    subject_prefix = "[ALERTE SECURITE 403]" if is_security_alert else "[ALERTE]"

    # === HTML ===
    html = f"""
    <html>
    <body style="font-family:Arial;background:#f4f4f4;padding:20px">
      <div style="max-width:700px;margin:auto;background:#fff;border-radius:8px;overflow:hidden">

        <div style="background:#c0392b;padding:20px;color:#fff">
          <h2 style="margin:0">{alert_title}</h2>
          <p style="margin:4px 0 0">{now}</p>
        </div>

        <div style="padding:20px">
          <p style="font-weight:bold;color:#c0392b">{alert_intro}</p>
          <table style="width:100%;border-collapse:collapse">
            <tr>
              <td style="padding:8px;font-weight:bold">Type</td>
              <td style="padding:8px">{type(error).__name__}</td>
            </tr>
            <tr style="background:#f9f9f9">
              <td style="padding:8px;font-weight:bold">Message</td>
              <td style="padding:8px">{error}</td>
            </tr>
            <tr>
              <td style="padding:8px;font-weight:bold">Méthode</td>
              <td style="padding:8px">{method}</td>
            </tr>
            <tr style="background:#f9f9f9">
              <td style="padding:8px;font-weight:bold">URL</td>
              <td style="padding:8px">{url}</td>
            </tr>
            <tr>
              <td style="padding:8px;font-weight:bold">Utilisateur</td>
              <td style="padding:8px">{user_id or "anonyme"}</td>
            </tr>
          </table>

          <h3 style="color:#c0392b;margin-top:20px">Stack trace</h3>
          <pre style="background:#2c3e50;color:#ecf0f1;padding:12px;border-radius:6px;
                      font-size:12px;overflow-x:auto;white-space:pre-wrap">
{tb}
          </pre>
        </div>

        <div style="padding:10px 20px;background:#f9f9f9;color:#888;font-size:12px">
          Alerte automatique – Backend &nbsp;|&nbsp; Ne pas répondre
        </div>

      </div>
    </body>
    </html>
    """

    # === TEXT fallback (important pour certains clients mail) ===
    text = f"""
    {alert_title}

    {alert_intro}

    Date: {now}
    Type: {type(error).__name__}
    Message: {error}
    Méthode: {method}
    URL: {url}
    User: {user_id or "anonyme"}

    Stack trace:
    {tb}
    """

    # === EMAIL ===
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{subject_prefix} {type(error).__name__} - {method} {url}"
    msg["From"] = smtp_user
    msg["To"] = admin_email

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # === SEND ===
    try:
        _log.info(
            "[ERROR ALERT] Envoi email: host=%s port=%s tls=%s from=%s to=%s url=%s",
            smtp_host,
            smtp_port,
            smtp_use_tls,
            smtp_user,
            admin_email,
            url,
        )
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, admin_email, msg.as_string())

        _log.info("[ERROR ALERT] Email envoye")
        print("[ERROR ALERT] Email envoye")

    except Exception as e:
        _log.exception("[ERROR ALERT] Erreur envoi mail: %s", e)
        print("[ERROR ALERT] Erreur envoi mail:", e)
