# app/services/email_service.py
import os
import smtplib
from email.mime.text import MIMEText
from typing import Protocol, runtime_checkable

@runtime_checkable
class EmailService(Protocol):
    def send_verification_email(self, recipient_email: str, verification_link: str) -> None:
        ...
    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        ...

class SMTPMailer:
    """SMTP implementation that supports verification + general email sending."""

    def __init__(self, smtp_host=None, smtp_port=None, username=None, password=None, from_addr=None):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(smtp_port or os.getenv("SMTP_PORT", 587))
        self.username = username or os.getenv("SMTP_USERNAME")
        self.password = password or os.getenv("SMTP_PASSWORD")
        self.from_addr = from_addr or os.getenv("SMTP_FROM") or self.username

    def _send(self, recipient_email: str, subject: str, body: str):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.from_addr
        msg["To"] = recipient_email
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.send_message(msg)

    def send_verification_email(self, recipient_email: str, verification_link: str) -> None:
        body = f"Please verify your email by visiting: {verification_link}\n\nIf you did not request this, ignore."
        self._send(recipient_email, "Verify your account", body)

    def send_email(self, recipient_email: str, subject: str, body: str) -> None:
        self._send(recipient_email, subject, body)

class MockMailer:
    """In-memory mock mailer for dev/tests."""

    def __init__(self):
        self.sent = []

    def send_verification_email(self, recipient_email: str, verification_link: str):
        self.sent.append({"type": "verification", "to": recipient_email, "link": verification_link})

    def send_email(self, recipient_email: str, subject: str, body: str):
        self.sent.append({"type": "generic", "to": recipient_email, "subject": subject, "body": body})
