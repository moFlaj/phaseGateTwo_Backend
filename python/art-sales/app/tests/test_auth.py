import pytest
from app import create_app, mongo
from app.config.db_config import TestConfig
from bson.objectid import ObjectId
import jwt


@pytest.fixture
def app():
    app = create_app(config_class=TestConfig)

    # Clean test DB before each test run
    with app.app_context():
        db = mongo.cx[TestConfig.DB_NAME]
        db.users.delete_many({})  # empty users collection before each test

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_signup_success(client):

    signup_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "StrongPass123",
        "role": "buyer"
    }

    response = client.post('/auth/signup', json=signup_data)


    assert response.status_code == 201

    # Assert JSON response success is true and contains user_id
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "user_id" in json_data
    assert ObjectId.is_valid(json_data["user_id"])

def test_signup_duplicate_email(client):
    signup_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "StrongPass123",
        "role": "buyer"
    }

    # First signup should succeed
    response1 = client.post('/auth/signup', json=signup_data)
    assert response1.status_code == 201

    # Second signup with same email should fail
    response2 = client.post('/auth/signup', json=signup_data)
    assert response2.status_code == 409  # Conflict

    json_data = response2.get_json()
    assert json_data["success"] is False
    assert json_data["message"] == "Email already in use."

def test_signup_missing_required_field(client):
    signup_data = {
        # "name" is missing
        "email": "missingname@example.com",
        "password": "MissingName123",
        "role": "buyer"
    }

    response = client.post('/auth/signup', json=signup_data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "name" in json_data["message"]


def test_signup_invalid_email_format(client):
    signup_data = {
        "name": "Invalid Email",
        "email": "invalid-email-format",
        "password": "ValidPassword123",
        "role": "buyer"
    }

    response = client.post('/auth/signup', json=signup_data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "email" in json_data["message"]


def test_signup_weak_password(client):
    signup_data = {
        "name": "Weak Password User",
        "email": "weakpass@example.com",
        "password": "123",  # too short
        "role": "artist"
    }

    response = client.post('/auth/signup', json=signup_data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert json_data["message"] == "Password must be at least 6 characters"


def test_login_success(app, client):
    """
    TDD step 1 - make signup then login succeed and token contains correct payload.
    """
    # 1. Register a user (setup for login)
    signup_data = {
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "StrongPass123",
        "role": "buyer"
    }
    # call the existing signup endpoint - this uses your signup code
    r = client.post("/auth/signup", json=signup_data)
    assert r.status_code == 201  # signup must succeed for login test

    # 2. Call /auth/login with same credentials
    login_data = {"email": signup_data["email"], "password": signup_data["password"]}
    r2 = client.post("/auth/login", json=login_data)

    # EXPECTED: 200 OK + access token
    assert r2.status_code == 200
    json_data = r2.get_json()
    assert json_data["success"] is True
    assert "access_token" in json_data and json_data["access_token"]

    # 3. Inspect token payload to ensure it has user_id and role
    token = json_data["access_token"]
    decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    # user_id should be a valid ObjectId string
    assert "user_id" in decoded and ObjectId.is_valid(decoded["user_id"])
    assert decoded.get("role") == signup_data["role"]


def test_login_invalid_credentials(client):
    """
    TDD step 2 - request with invalid credentials returns 401 with generic message.
    """
    login_data = {"email": "noone@example.com", "password": "wrong"}
    r = client.post("/auth/login", json=login_data)

    # EXPECTED: 401 Unauthorized (do not reveal whether email exists)
    assert r.status_code == 401
    json_data = r.get_json()
    assert json_data["success"] is False
    assert "Invalid email or password" in json_data["message"]

