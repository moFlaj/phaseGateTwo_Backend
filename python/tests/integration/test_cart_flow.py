import json
import pytest
from app.shared.utilities.token_manager import TokenManager

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

def test_add_and_get_cart(client, buyer_jwt, artist_jwt):
    # First create an artwork as artist
    create = post_json(client, "/api/artist/works", {"title":"CartArt","price":250.0}, jwt=artist_jwt)
    art_id = create.get_json()["artwork_id"]

    # Add item to cart
    item = {
        "artwork_id": art_id,
        "quantity": 2
    }
    resp = client.post("/api/cart/add", json=item, headers={"Authorization": buyer_jwt})
    data = json.loads(resp.data)

    assert resp.status_code == 201
    assert data["success"]

    # Get cart
    resp2 = client.get("/api/cart/", headers={"Authorization": buyer_jwt})
    data2 = json.loads(resp2.data)
    assert resp2.status_code == 200
    assert "cart" in data2
    assert len(data2["cart"]["items"]) >= 1
