# app/jobs/email_jobs.py
from redis import Redis
from rq import Queue
import os
from typing import Optional
from app.shared.utilities.email_service import SMTPMailer


def get_redis_connection() -> Redis:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(redis_url)


def enqueue_email_job(email: str, verification_link: str) -> None:
    q = Queue("emails", connection=get_redis_connection())
    q.enqueue("app.jobs.email_jobs.send_verification_email", email,
              verification_link)


def send_verification_email(email: str, verification_link: str) -> None:
    # Worker process instantiates SMTPMailer using environment variables (no Flask app needed)
    smtp = SMTPMailer()
    smtp.send_verification_email(email, verification_link)
