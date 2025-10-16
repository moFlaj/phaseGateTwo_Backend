import json
from tests.utils.auth_test_utils import (
    signup_payload,
    verify_payload,
    post_json,
    extract_code_from_mock_mailer,
)
from app.extensions import mongo
from flask import current_app


class TestAuthEdgeCases:
    """Edge case and validation integration tests for auth routes."""

    def test_signup_missing_email(self, client):
        data = signup_payload()
        data["email"] = ""
        resp = post_json(client, "/api/auth/signup", data)
        res = json.loads(resp.data)
        assert resp.status_code == 400
        assert "email" in res["message"].lower()

    def test_signup_weak_password(self, client):
        data = signup_payload()
        data["password"] = "123"
        resp = post_json(client, "/api/auth/signup", data)
        res = json.loads(resp.data)
        assert resp.status_code == 400
        assert "password" in res["message"].lower()

    def test_signup_invalid_role(self, client):
        data = signup_payload()
        data["role"] = "superhero"
        resp = post_json(client, "/api/auth/signup", data)
        res = json.loads(resp.data)
        assert resp.status_code == 400
        assert "role" in res["message"].lower()

    def test_verify_missing_code(self, client):
        data = signup_payload(email="missingcode@example.com")
        post_json(client, "/api/auth/signup", data)
        missing = {
            "email": "missingcode@example.com",
            "name": "NoCode",
            "password": "StrongPass123",
            "role": "buyer"
        }
        resp = post_json(client, "/api/auth/verify", missing)
        res = json.loads(resp.data)
        assert resp.status_code == 400
        assert "code" in res["message"].lower()

    def test_verify_already_verified_user(self, client, app):
        email = "twice@example.com"
        post_json(client, "/api/auth/signup", signup_payload(email=email))
        code = extract_code_from_mock_mailer(email, app)
        # first verification
        verify_data = verify_payload("User", email, code)
        post_json(client, "/api/auth/verify", verify_data)
        # second attempt
        resp = post_json(client, "/api/auth/verify", verify_data)
        res = json.loads(resp.data)
        assert resp.status_code == 404
        assert "verification" in res["message"].lower()

    def test_login_nonexistent_user(self, client):
        data = {"email": "ghost@example.com", "password": "NoExist123"}
        resp = post_json(client, "/api/auth/login", data)
        res = json.loads(resp.data)
        assert resp.status_code == 401
        assert "email not registered" in res["message"].lower()