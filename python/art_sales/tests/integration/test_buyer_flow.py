# tests/integration/test_buyer_flow.py
import json
import pytest
from app.shared.utilities.token_manager import TokenManager
from app.extensions import mongo

@pytest.fixture(autouse=True)
def clear_orders_and_artworks(app):
    db = mongo.cx[app.config['DB_NAME']]
    db['orders'].delete_many({})
    db['artworks'].delete_many({})
    yield
    db['orders'].delete_many({})
    db['artworks'].delete_many({})

@pytest.fixture()
def buyer_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('buyer@example.com','buyer', app.config['SECRET_KEY'])}"

@pytest.fixture()
def artist_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('artist@example.com','artist', app.config['SECRET_KEY'])}"

def post_json(client, url, data, jwt=None):
    headers = {"Content-Type": "application/json"}
    if jwt: headers["Authorization"]=jwt
    return client.post(url, data=json.dumps(data), headers=headers)

def get_json(client, url, jwt=None):
    headers = {}
    if jwt: headers["Authorization"]=jwt
    return client.get(url, headers=headers)

def test_create_order_success(client, artist_jwt, buyer_jwt):
    # First create an artwork as artist
    create = post_json(client, "/api/artist/works", {"title":"BuyerArt","price":100.0}, jwt=artist_jwt)
    art_id = create.get_json()["artwork_id"]

    # Buyer creates order
    payload = {"artwork_id": art_id, "quantity": 2}
    resp = post_json(client, "/api/buyer/orders", payload, jwt=buyer_jwt)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert "order_id" in data

def test_create_order_invalid_artwork(client, buyer_jwt):
    payload = {"artwork_id": "507f191e810c19729de860ea", "quantity": 1}
    resp = post_json(client, "/api/buyer/orders", payload, jwt=buyer_jwt)
    assert resp.status_code == 404

def test_list_orders(client, artist_jwt, buyer_jwt):
    # create one artwork and one order
    create = post_json(client, "/api/artist/works", {"title":"ListArt","price":50.0}, jwt=artist_jwt)
    art_id = create.get_json()["artwork_id"]
    post_json(client, "/api/buyer/orders", {"artwork_id": art_id, "quantity": 1}, jwt=buyer_jwt)

    resp = get_json(client, "/api/buyer/orders", jwt=buyer_jwt)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["orders"], list)
    assert len(data["orders"]) == 1

def test_create_order_unauthenticated(client):
    payload = {"artwork_id": "507f191e810c19729de860ea", "quantity": 1}
    resp = client.post("/api/buyer/orders", json=payload)
    assert resp.status_code == 401


def test_buyer_list_orders(client, app, buyer_jwt, seed_mongo_data):
    """Buyer can view their orders."""
    resp = client.get("/api/buyer/orders", headers={"Authorization": buyer_jwt})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert len(data["orders"]) >= 1
    assert "buyer@example.com" in [o["buyer_id"] for o in data["orders"]]

def test_buyer_summary(client, app, buyer_jwt, seed_mongo_data):
    """Buyer dashboard shows correct totals."""
    resp = client.get("/api/buyer/dashboard", headers={"Authorization": buyer_jwt})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["success"] is True
    summary = data["summary"]
    assert summary["total_orders"] >= 1
    assert summary["completed_orders"] >= 1



