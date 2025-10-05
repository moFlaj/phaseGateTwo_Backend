
import uuid

def signup_and_login(client, role="buyer", email=None, password="StrongPass123"):
    """
    Helper to create a unique user and log them in, returning a valid JWT token.
    """
    # Always generate a unique email if not provided
    if email is None:
        unique_suffix = uuid.uuid4().hex[:6]
        email = f"{role}_user_{unique_suffix}@example.com"

    # Signup
    signup_data = {
        "name": f"{role.capitalize()} Test User",
        "email": email,
        "password": password,
        "role": role
    }
    signup_response = client.post('/auth/signup', json=signup_data)
    assert signup_response.status_code in (200, 201), f"Signup failed: {signup_response.get_data(as_text=True)}"

    # Login
    login_data = {"email": email, "password": password}
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 200, f"Login failed: {response.get_data(as_text=True)}"

    json_data = response.get_json()
    assert json_data["success"] is True
    assert "access_token" in json_data
    return json_data["access_token"]
