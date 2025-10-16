import json
import pytest
from app.shared.utilities.token_manager import TokenManager
from app.extensions import mongo


@pytest.fixture(autouse=True)
def clear_orders_artworks(app):
    """Ensure clean DB for every test."""
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
def artist_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('artist@example.com', 'artist', app.config['SECRET_KEY'])}"


@pytest.fixture()
def other_artist_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('intruder@example.com', 'artist', app.config['SECRET_KEY'])}"


def post_json(client, url, data, jwt=None):
    headers = {"Content-Type": "application/json"}
    if jwt:
        headers["Authorization"] = jwt
    return client.post(url, data=json.dumps(data), headers=headers)


def put_json(client, url, data=None, jwt=None):
    headers = {"Content-Type": "application/json"}
    if jwt:
        headers["Authorization"] = jwt
    return client.put(url, data=json.dumps(data or {}), headers=headers)


def get_json(client, url, jwt=None):
    headers = {}
    if jwt:
        headers["Authorization"] = jwt
    return client.get(url, headers=headers)


# --- TESTS ---


def test_artist_can_complete_own_order(client, artist_jwt, buyer_jwt):
    """Artist successfully marks their own order as shipped."""
    # Create artwork
    art_resp = post_json(client, "/api/artist/works", {"title": "Art1", "price": 100.0}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]

    # Buyer places order
    order_resp = post_json(client, "/api/buyer/orders", {"artwork_id": art_id, "quantity": 1}, jwt=buyer_jwt)
    order_id = order_resp.get_json()["order_id"]

    # Artist ships the order (new flow)
    ship_resp = client.post(f"/api/artist/orders/{order_id}/ship", headers={"Authorization": artist_jwt})
    data = ship_resp.get_json()
    assert ship_resp.status_code == 200
    assert data["success"] is True
    assert "shipped" in data["message"].lower()

    # Buyer confirms receipt (new flow)
    confirm_resp = client.post(f"/api/buyer/orders/{order_id}/confirm", headers={"Authorization": buyer_jwt})
    confirm_data = confirm_resp.get_json()
    assert confirm_resp.status_code == 200
    assert confirm_data["success"] is True
    assert "confirmed" in confirm_data["message"].lower()


def test_artist_cannot_complete_someone_elses_order(client, artist_jwt, other_artist_jwt, buyer_jwt):
    """Artist cannot ship another artist's order."""
    # Artist A creates artwork
    art_resp = post_json(client, "/api/artist/works", {"title": "Forbidden", "price": 100.0}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]

    # Buyer orders it
    order_resp = post_json(client, "/api/buyer/orders", {"artwork_id": art_id}, jwt=buyer_jwt)
    order_id = order_resp.get_json()["order_id"]

    # Artist B tries to ship
    resp = client.post(f"/api/artist/orders/{order_id}/ship", headers={"Authorization": other_artist_jwt})
    data = resp.get_json()
    assert resp.status_code == 403
    assert "cannot update another artist" in data["message"].lower()


def test_complete_nonexistent_order_returns_404(client, artist_jwt):
    """Completing an invalid order should raise 404."""
    resp = put_json(client, "/api/artist/orders/507f191e810c19729de860ea/complete", jwt=artist_jwt)
    data = resp.get_json()
    assert resp.status_code == 404
    assert "order not found" in data["message"].lower()


def test_cannot_complete_order_twice(client, artist_jwt, buyer_jwt):
    """Order already shipped -> ValidationError (400)."""
    # Setup: create order and ship once
    art_resp = post_json(client, "/api/artist/works", {"title": "TwiceArt", "price": 50}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]

    order_resp = post_json(client, "/api/buyer/orders", {"artwork_id": art_id}, jwt=buyer_jwt)
    order_id = order_resp.get_json()["order_id"]

    client.post(f"/api/artist/orders/{order_id}/ship", headers={"Authorization": artist_jwt})  # first shipping
    second = client.post(f"/api/artist/orders/{order_id}/ship", headers={"Authorization": artist_jwt})
    data = second.get_json()
    assert second.status_code == 400
    assert "can only ship orders that are being processed" in data["message"].lower()


def test_dashboard_reflects_completed_earnings(client, artist_jwt, buyer_jwt):
    """Dashboard shows updated total_sales and earnings after shipping and confirmation."""
    # Create and order
    art_resp = post_json(client, "/api/artist/works", {"title": "EarningArt", "price": 200.0}, jwt=artist_jwt)
    art_id = art_resp.get_json()["artwork_id"]
    order_resp = post_json(client, "/api/buyer/orders", {"artwork_id": art_id, "quantity": 2}, jwt=buyer_jwt)
    order_id = order_resp.get_json()["order_id"]

    # Initially, dashboard shows no earnings
    dash1 = get_json(client, "/api/artist/dashboard", jwt=artist_jwt)
    d1 = dash1.get_json()["summary"]
    assert d1["earnings"] == 0.0

    # Ship the order (earnings still 0)
    client.post(f"/api/artist/orders/{order_id}/ship", headers={"Authorization": artist_jwt})
    dash2 = get_json(client, "/api/artist/dashboard", jwt=artist_jwt)
    d2 = dash2.get_json()["summary"]
    assert d2["earnings"] == 0.0  # Still 0 because not confirmed yet

    # Buyer confirms receipt (earnings updated)
    client.post(f"/api/buyer/orders/{order_id}/confirm", headers={"Authorization": buyer_jwt})
    dash3 = get_json(client, "/api/artist/dashboard", jwt=artist_jwt)
    d3 = dash3.get_json()["summary"]
    assert d3["earnings"] > 0.0
    assert d3["total_sales"] >= 1
