import os
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str) -> None:
    """Send a simple plaintext email using SMTP settings from env.

    Environment variables:
    - SMTP_HOST (default: localhost)
    - SMTP_PORT (default: 1025)
    - SMTP_USER (optional)
    - SMTP_PASSWORD (optional)
    - SMTP_FROM (default: noreply@tinko-local.dev)
    - SMTP_USE_TLS (default: false)
    """
    host = os.getenv("SMTP_HOST", "localhost")
    port = int(os.getenv("SMTP_PORT", "1025"))
    user = os.getenv("SMTP_USER") or None
    password = os.getenv("SMTP_PASSWORD") or None
    from_email = os.getenv("SMTP_FROM", "noreply@tinko-local.dev")
    use_tls = (os.getenv("SMTP_USE_TLS", "false").lower() in ("1", "true", "yes"))

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if use_tls:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as server:
            if user and password:
                server.login(user, password)
            server.send_message(msg)
