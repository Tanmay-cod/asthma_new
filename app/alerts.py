"""High-risk alert delivery via Telegram and/or Email.
Set environment variables to enable:
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
  ALERT_EMAIL_FROM, ALERT_EMAIL_TO, ALERT_EMAIL_PASSWORD, ALERT_SMTP_HOST (optional, default smtp.gmail.com), ALERT_SMTP_PORT
"""
import os
import time
import smtplib
from email.mime.text import MIMEText

_last_alert = {}  # user_id -> timestamp (cooldown)
COOLDOWN_SEC = int(os.environ.get("ALERT_COOLDOWN", "600"))


def _can_alert(user_id: int) -> bool:
    now = time.time()
    if now - _last_alert.get(user_id, 0) > COOLDOWN_SEC:
        _last_alert[user_id] = now
        return True
    return False


def send_telegram(message: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        import requests
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id": chat_id, "text": message}, timeout=10)
        return r.ok
    except Exception as e:
        print("Telegram alert failed:", e)
        return False


def send_email(subject: str, message: str) -> bool:
    frm = os.environ.get("ALERT_EMAIL_FROM")
    to = os.environ.get("ALERT_EMAIL_TO")
    pwd = os.environ.get("ALERT_EMAIL_PASSWORD")
    if not (frm and to and pwd):
        return False
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = frm
        msg["To"] = to
        with smtplib.SMTP_SSL(os.environ.get("ALERT_SMTP_HOST", "smtp.gmail.com"),
                              int(os.environ.get("ALERT_SMTP_PORT", "465"))) as s:
            s.login(frm, pwd)
            s.sendmail(frm, [to], msg.as_string())
        return True
    except Exception as e:
        print("Email alert failed:", e)
        return False


def maybe_alert(user_id: int, user_name: str, risk_score: float, risk_level: str):
    if risk_level != "High" or not _can_alert(user_id):
        return
    text = (f"⚠️ HIGH ASTHMA RISK for {user_name}!\n"
            f"Risk score: {risk_score}/100\n"
            f"Please check the dashboard immediately and consult a physician if symptoms persist.")
    send_telegram(text)
    send_email("⚠️ High Asthma Risk Alert", text)
    print(f"[ALERT] High risk alert sent for user {user_name} (score {risk_score})")
