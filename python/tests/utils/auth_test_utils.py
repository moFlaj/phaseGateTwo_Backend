import json
from flask import current_app


def signup_payload(name="Alice", email="alice@example.com"):
    return {
        "name": name,
        "email": email,
        "password": "StrongPass123",
        "role": "buyer",
    }

def login_payload(email, password="StrongPass123"):
    return {"email": email, "password": password}

def verify_payload(name, email, code, password="StrongPass123"):
    return {
        "name": name,
        "email": email,
        "password": password,
        "role": "buyer",
        "code": code,
    }

def extract_code_from_mock_mailer(email: str, app=None):
    if app:
        with app.app_context():
            email_service = app.config.get("EMAIL_SERVICE")
    else:
        email_service = current_app.config.get("EMAIL_SERVICE")
    
    if not email_service:
        return None

    for mail in getattr(email_service, "sent", []):
        if mail["to"] == email:
            link = mail["link"]
            link = link.strip()
            if "code =" in link:
                return link.split("code =")[1].strip()
    return None

def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")
