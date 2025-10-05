
from tests.conftest import client
from bson.objectid import ObjectId
from tests.helpers import signup_and_login


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
    response1 = client.post('/auth/signup', json=signup_data)
    assert response1.status_code == 201
    response2 = client.post('/auth/signup', json=signup_data)
    assert response2.status_code == 409
    json_data = response2.get_json()
    assert not json_data["success"]
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


def test_login_success(client):
    token = signup_and_login(client)
    assert token is not None



def test_login_wrong_password(client):
    signup_data = {
        "name": "Wrong Password User",
        "email": "wrongpass@example.com",
        "password": "RightPass123",
        "role": "buyer"
    }
    client.post('/auth/signup', json=signup_data)

    login_data = {"email": "wrongpass@example.com", "password": "WrongPass999"}
    response = client.post('/auth/login', json=login_data)

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Invalid email or password" in json_data["message"]


def test_login_nonexistent_email(client):
    login_data = {"email": "doesnotexist@example.com", "password": "Whatever123"}
    response = client.post('/auth/login', json=login_data)

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Invalid email or password" in json_data["message"]


# ======================
# PROTECTED ROUTES TESTS
# ======================

def test_protected_endpoint_requires_token(client):
    r = client.get("/artist/dashboard")
    assert r.status_code == 401
    assert "Authorization" in r.get_json()["message"]


def test_protected_endpoint_with_valid_artist_token(client):
    token = signup_and_login(client, "artist")
    r = client.get("/artist/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json()["success"] is True


def test_protected_endpoint_with_invalid_token(client):
    r = client.get("/artist/dashboard", headers={"Authorization": "Bearer not_a_real_token"})
    assert r.status_code == 401
    json_data = r.get_json()
    assert json_data["success"] is False
    assert "Invalid token" in json_data["message"]


def test_protected_endpoint_wrong_role(client):
    token = signup_and_login(client, role="buyer")
    r = client.get("/artist/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


# ====== BUYER PROTECTED ROUTES TESTS ======
def test_buyer_protected_requires_token(client):
    """
    No Authorization header -> 401
    """
    r = client.get("/buyer/dashboard")
    assert r.status_code == 401
    assert "Authorization" in r.get_json()["message"]


def test_buyer_endpoint_with_valid_buyer_token(client):
    """
    Buyer token -> 200 OK
    """
    token = signup_and_login(client, role="buyer")
    print("\nTOKEN:", token)
    r = client.get("/buyer/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    json_data = r.get_json()
    assert json_data["success"] is True


def test_buyer_endpoint_with_invalid_token(client):
    """
    Invalid token -> 401
    """
    r = client.get("/buyer/dashboard", headers={"Authorization": "Bearer totally_wrong"})
    assert r.status_code == 401
    json_data = r.get_json()
    assert json_data["success"] is False
    assert "Invalid token" in json_data["message"]


def test_buyer_endpoint_forbidden_for_artist(client):
    """
    An artist token trying to call buyer endpoint -> 403
    """
    token = signup_and_login(client, role="artist")
    r = client.get("/buyer/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
    json_data = r.get_json()
    assert json_data["success"] is False
    assert "Forbidden" in json_data["message"]
