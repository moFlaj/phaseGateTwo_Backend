import json
import pytest
from app.shared.utilities.token_manager import TokenManager
from app.extensions import mongo


@pytest.fixture(autouse=True)
def clear_db(app):
    """Reset collections before each test."""
    db = mongo.cx[app.config["DB_NAME"]]
    db["orders"].delete_many({})
    db["artworks"].delete_many({})
    yield
    db["orders"].delete_many({})
    db["artworks"].delete_many({})


@pytest.fixture()
def buyer_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('buyer@example.com', 'buyer', app.config['SECRET_KEY'])}"


@pytest.fixture()
def other_buyer_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('second@example.com', 'buyer', app.config['SECRET_KEY'])}"


@pytest.fixture()
def artist_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('artist@example.com', 'artist', app.config['SECRET_KEY'])}"


def post_json(client, url, data, jwt=None):
    headers = {"Content-Type": "application/json"}
    if jwt:
        headers["Authorization"] = jwt
    return client.post(url, data=json.dumps(data), headers=headers)


def get_json(client, url, jwt=None):
    headers = {}
    if jwt:
        headers["Authorization"] = jwt
    return client.get(url, headers=headers)


# --- TEST CASES ---


def test_order_nonexistent_artwork_returns_404(client, buyer_jwt):
    """Buyer cannot order an artwork that doesn't exist."""
    resp = post_json(client, "/api/buyer/orders", {"artwork_id": "507f191e810c19729de860ea"}, jwt=buyer_jwt)
    data = resp.get_json()
    assert resp.status_code == 404
    assert "artwork not found" in data["message"].lower()


def test_duplicate_order_returns_400(client, buyer_jwt, artist_jwt):
    """Buyer cannot order same artwork twice."""
    # Artist uploads artwork
    art_resp = post_json(client, "/api/artist/works", {"title": "UniqueArt", "price": 120}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]

    # Buyer orders once
    post_json(client, "/api/buyer/orders", {"artwork_id": art_id, "quantity": 1}, jwt=buyer_jwt)

    # Buyer tries again
    dup_resp = post_json(client, "/api/buyer/orders", {"artwork_id": art_id, "quantity": 1}, jwt=buyer_jwt)
    data = dup_resp.get_json()
    assert dup_resp.status_code == 400
    assert "already ordered" in data["message"].lower()


@pytest.mark.parametrize("qty", [0, -1])
def test_invalid_quantity_returns_400(client, buyer_jwt, artist_jwt, qty):
    """Quantity must be > 0."""
    art_resp = post_json(client, "/api/artist/works", {"title": "BadQty", "price": 30}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]

    resp = post_json(client, "/api/buyer/orders", {"artwork_id": art_id, "quantity": qty}, jwt=buyer_jwt)
    data = resp.get_json()
    assert resp.status_code == 400
    assert "quantity must be" in data["message"].lower()


def test_artist_cannot_place_order(client, artist_jwt):
    """Artist cannot use buyer endpoint."""
    resp = post_json(client, "/api/buyer/orders", {"artwork_id": "123"}, jwt=artist_jwt)
    data = resp.get_json()
    assert resp.status_code == 403
    assert "forbidden" in data["message"].lower()


def test_buyer_can_list_own_orders(client, buyer_jwt, artist_jwt):
    """Buyer can see their own orders."""
    art_resp = post_json(client, "/api/artist/works", {"title": "MyArt", "price": 70}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]
    post_json(client, "/api/buyer/orders", {"artwork_id": art_id, "quantity": 2}, jwt=buyer_jwt)

    resp = get_json(client, "/api/buyer/orders", jwt=buyer_jwt)
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data["orders"]) == 1


def test_buyer_cannot_view_others_orders(client, buyer_jwt, other_buyer_jwt, artist_jwt):
    """Buyers can only view their own orders."""
    art_resp = post_json(client, "/api/artist/works", {"title": "PrivateArt", "price": 55}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]

    # Buyer1 creates order
    post_json(client, "/api/buyer/orders", {"artwork_id": art_id}, jwt=buyer_jwt)

    # Buyer2 tries to fetch - should only see their own orders (none)
    resp = get_json(client, "/api/buyer/orders", jwt=other_buyer_jwt)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["success"] is True
    assert len(data["orders"]) == 0  # Buyer2 should see no orders since they haven't placed any


def test_unauthorized_request_returns_401(client):
    """Missing Authorization header should raise 401."""
    resp = get_json(client, "/api/buyer/orders")
    data = resp.get_json()
    assert resp.status_code == 401
    assert "missing" in data["message"].lower()
