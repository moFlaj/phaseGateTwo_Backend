import pytest
from app import create_app, mongo
from app.config.db_config import TestConfig
from bson.objectid import ObjectId


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

