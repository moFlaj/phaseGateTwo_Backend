# app/tests/helpers.py
def signup_and_login(client, role="buyer", email=None, password="StrongPass123"):
    """
    Helper to create a user and login, returning the access token.
    """
    if email is None:
        email = "loginuser@example.com"
    # First signup
    signup_data = {
        "name": "Login User",
        "email": email,
        "password": password,
        "role": role
    }
    client.post('/auth/signup', json=signup_data)

    # Then login
    login_data = {"email": "loginuser@example.com", "password": "StrongPass123"}
    response = client.post('/auth/login', json=login_data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "access_token" in json_data
    return json_data["access_token"]
