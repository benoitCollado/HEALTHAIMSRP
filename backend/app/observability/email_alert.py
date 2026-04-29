import os
import smtplib
import traceback
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

# ==============================
# CONFIG
# ==============================

_last_sent: dict[str, datetime] = {}
_COOLDOWN_SECONDS = 60


# ==============================
# UTILS
# ==============================

def _is_on_cooldown(error_key: str) -> bool:
    last = _last_sent.get(error_key)
    if last is None:
        return False
    return (datetime.utcnow() - last).total_seconds() < _COOLDOWN_SECONDS


def _get_stacktrace(error: Exception) -> str:
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
    user_id: Optional[int] = None,
) -> None:
    """
    Envoie un email d'alerte en cas d'erreur backend.
    """

    # === ENV ===
    smtp_user = os.getenv("EMAIL_USER") or os.getenv("ADMIN_EMAIL")
    smtp_password = os.getenv("EMAIL_PASS")
    admin_email = os.getenv("ADMIN_EMAIL")

    if not all([smtp_user, smtp_password, admin_email]):
        print("[ERROR ALERT] SMTP non configuré")
        return

    # === Anti spam ===
    error_key = f"{type(error).__name__}:{url}"
    if _is_on_cooldown(error_key):
        return
    _last_sent[error_key] = datetime.utcnow()

    # === DATA ===
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    tb = _get_stacktrace(error)

    # === HTML ===
    html = f"""
    <html>
    <body style="font-family:Arial;background:#f4f4f4;padding:20px">
      <div style="max-width:700px;margin:auto;background:#fff;border-radius:8px;overflow:hidden">

        <div style="background:#c0392b;padding:20px;color:#fff">
          <h2 style="margin:0">⚠ Erreur API</h2>
          <p style="margin:4px 0 0">{now}</p>
        </div>

        <div style="padding:20px">
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
    Erreur API

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
    msg["Subject"] = f"[ALERTE] {type(error).__name__} - {method} {url}"
    msg["From"] = smtp_user
    msg["To"] = admin_email

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # === SEND ===
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, admin_email, msg.as_string())

        print("[ERROR ALERT] Email envoyé")

    except Exception as e:
        print("[ERROR ALERT] Erreur envoi mail:", e)