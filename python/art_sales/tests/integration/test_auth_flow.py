import json
from tests.utils.auth_test_utils import (
    signup_payload,
    login_payload,
    verify_payload,
    post_json,
    extract_code_from_mock_mailer,
)


class TestAuthIntegration:
    """Full integration tests for Auth routes using real app context + MockMailer."""

    def test_signup_success(self, client, app):
        resp = post_json(client, "/api/auth/signup", signup_payload())
        data = json.loads(resp.data)
        assert resp.status_code == 202
        assert data["success"] is True
        assert "Verification" in data["message"]

        # verify mail sent
        email = signup_payload()["email"]
        code = extract_code_from_mock_mailer(email, app)
        assert code is not None and code.isdigit()

    def test_signup_duplicate_email(self, client, app):
        email = "bob@example.com"
        payload = signup_payload(email = email)
        post_json(client, "/api/auth/signup", payload)
        code = extract_code_from_mock_mailer(email, app)
        assert code is not None
        verify_data = verify_payload("Bob", email, code)
        post_json(client, "/api/auth/verify", verify_data)
        resp = post_json(client, "/api/auth/signup", payload)
        data = json.loads(resp.data)
        assert resp.status_code == 409
        assert data["success"] is False
        assert "exists" in data["message"].lower()

    def test_verify_success(self, client, app):
        email = "eve@example.com"
        # signup first
        post_json(client, "/api/auth/signup", signup_payload(name="Eve", email=email))
        code = extract_code_from_mock_mailer(email, app)
        assert code is not None

        verify_data = verify_payload("Eve", email, code)
        resp = post_json(client, "/api/auth/verify", verify_data)
        data = json.loads(resp.data)
        assert resp.status_code == 201
        assert data["success"] is True
        assert "User created" in data["message"]

    def test_verify_invalid_code(self, client, app):
        email = "zoe@example.com"
        post_json(client, "/api/auth/signup", signup_payload(name="Zoe", email=email))
        verify_data = verify_payload("Zoe", email, code="000000")
        resp = post_json(client, "/api/auth/verify", verify_data)
        assert resp.status_code == 400

    def test_verify_nonexistent_email(self, client, app):
        verify_data = verify_payload("NonUser", "nouser@example.com", "999999")
        resp = post_json(client, "/api/auth/verify", verify_data)
        assert resp.status_code == 404

    def test_login_success(self, client, app):
        email = "tom@example.com"
        # signup and verify
        post_json(client, "/api/auth/signup", signup_payload(name="Tom", email=email))
        code = extract_code_from_mock_mailer(email, app)
        verify_data = verify_payload("Tom", email, code)
        post_json(client, "/api/auth/verify", verify_data)

        resp = post_json(client, "/api/auth/login", login_payload(email))
        data = json.loads(resp.data)
        assert resp.status_code == 200
        assert data["success"] is True
        assert "access_token" in data

    def test_login_wrong_password(self, client, app):
        email = "leo@example.com"
        post_json(client, "/api/auth/signup", signup_payload(name="Leo", email=email))
        code = extract_code_from_mock_mailer(email, app)
        post_json(client, "/api/auth/verify", verify_payload("Leo", email, code))

        wrong_pw = {"email": email, "password": "WrongPass"}
        resp = post_json(client, "/api/auth/login", wrong_pw)
        data = json.loads(resp.data)
        assert resp.status_code == 401
        assert not data["success"]

    def test_wallet_created_after_signup(self, client, app):
        """Test that a wallet is automatically created after successful signup and verification."""
        email = "wallettest@example.com"
        # Signup first
        post_json(client, "/api/auth/signup", signup_payload(name="WalletTest", email=email))
        code = extract_code_from_mock_mailer(email, app)
        
        # Verify user (this should create a wallet)
        verify_data = verify_payload("WalletTest", email, code)
        resp = post_json(client, "/api/auth/verify", verify_data)
        assert resp.status_code == 201
        
        # Login to get user ID
        login_resp = post_json(client, "/api/auth/login", login_payload(email))
        login_data = json.loads(login_resp.data)
        assert login_resp.status_code == 200
        user_id = login_data.get("user_id")
        assert user_id is not None
        
        # Check that wallet was created by trying to access wallet balance
        # We need to set the user ID in headers to access the wallet
        from app.wallet.controllers.wallet_controller import wallet_service
        if wallet_service:
            wallet = wallet_service.get_wallet(user_id)
            assert wallet is not None
            assert wallet.user_id == user_id
            assert wallet.balance == 0.0

    def test_buyer_dashboard_includes_wallet_info(self, client, app):
        """Test that the buyer dashboard includes wallet information."""
        email = "dashboardtest@example.com"
        # Signup and verify user
        post_json(client, "/api/auth/signup", signup_payload(name="DashboardTest", email=email))
        code = extract_code_from_mock_mailer(email, app)
        post_json(client, "/api/auth/verify", verify_payload("DashboardTest", email, code))
        
        # Login to get token
        login_resp = post_json(client, "/api/auth/login", login_payload(email))
        login_data = json.loads(login_resp.data)
        assert login_resp.status_code == 200
        token = login_data.get("access_token")
        user_id = login_data.get("user_id")
        assert token is not None
        assert user_id is not None
        
        # Access buyer dashboard with token
        headers = {
            "Authorization": f"Bearer {token}"
        }
        dashboard_resp = client.get("/api/buyer/dashboard", headers=headers)
        assert dashboard_resp.status_code == 200
        
        # Check that dashboard response includes wallet information
        dashboard_data = json.loads(dashboard_resp.data)
        assert dashboard_data["success"] is True
        assert "summary" in dashboard_data
        summary = dashboard_data["summary"]
        assert "wallet_balance" in summary
        assert "wallet_currency" in summary
        # Since this is a buyer, we expect the wallet to be created with 0 balance
        assert summary["wallet_balance"] == 0.0
        assert summary["wallet_currency"] == "NGN"

    def test_artist_dashboard_includes_wallet_info(self, client, app):
        """Test that the artist dashboard includes wallet information."""
        email = "artistdashboard@example.com"
        # Signup and verify artist
        signup_data = signup_payload(name="ArtistDashboard", email=email)
        signup_data["role"] = "artist"
        post_json(client, "/api/auth/signup", signup_data)
        code = extract_code_from_mock_mailer(email, app)
        verify_data = verify_payload("ArtistDashboard", email, code)
        verify_data["role"] = "artist"
        post_json(client, "/api/auth/verify", verify_data)
        
        # Login to get token
        login_resp = post_json(client, "/api/auth/login", login_payload(email))
        login_data = json.loads(login_resp.data)
        assert login_resp.status_code == 200
        token = login_data.get("access_token")
        user_id = login_data.get("user_id")
        assert token is not None
        assert user_id is not None
        
        # Access artist dashboard with token
        headers = {
            "Authorization": f"Bearer {token}"
        }
        dashboard_resp = client.get("/api/artist/dashboard", headers=headers)
        assert dashboard_resp.status_code == 200
        
        # Check that dashboard response includes wallet information
        dashboard_data = json.loads(dashboard_resp.data)
        assert dashboard_data["success"] is True
        assert "summary" in dashboard_data
        summary = dashboard_data["summary"]
        assert "wallet_balance" in summary
        assert "wallet_currency" in summary
        # Since this is an artist, we expect the wallet to be created with 0 balance
        assert summary["wallet_balance"] == 0.0
        assert summary["wallet_currency"] == "NGN"
