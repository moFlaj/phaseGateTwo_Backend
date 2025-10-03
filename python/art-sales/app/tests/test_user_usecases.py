import pytest
from app.tests.helpers import signup_and_login
from app.tests.conftest import client


def test_buyer_order_history_empty(client):
    token = signup_and_login(client, "buyer")
    r = client.get("/buyer/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["orders"] == []


def test_buyer_cart_add_and_get(client):
    token = signup_and_login(client, role="buyer")
    artwork_id = "artwork123"
    r1 = client.post("/buyer/cart", headers={"Authorization": f"Bearer {token}"}, json={"artwork_id": artwork_id, "quantity": 2})
    assert r1.status_code == 201
    r2 = client.get("/buyer/cart", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.get_json()
    assert any(item["artwork_id"] == artwork_id for item in data["items"])


def test_buyer_profile_update(client):
    token = signup_and_login(client, role="buyer")
    update_data = {"name": "Updated Buyer", "password": "NewStrongPass123"}
    r = client.put("/buyer/profile", headers={"Authorization": f"Bearer {token}"}, json=update_data)
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True


def test_artist_upload_and_dashboard(client):
    token = signup_and_login(client, role="artist")

    # Upload artwork
    artwork_data = {"title": "Sunset", "price": 100.0, "image_url": "http://example.com/sunset.jpg"}
    r1 = client.post("/artist/artwork", headers={"Authorization": f"Bearer {token}"}, json=artwork_data)
    assert r1.status_code == 201
    json_data = r1.get_json()
    artwork_id = json_data["artwork_id"]
    assert json_data["success"] is True

    # Check dashboard lists artwork
    r2 = client.get("/artist/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.get_json()
    assert any(a["title"] == "Sunset" for a in data["artworks"])


def test_artist_update_and_delete_artwork(client):
    token = signup_and_login(client, role="artist")

    artwork_data = {"title": "Morning", "price": 50.0, "image_url": "http://example.com/morning.jpg"}
    r1 = client.post("/artist/artwork", headers={"Authorization": f"Bearer {token}"}, json=artwork_data)
    artwork_id = r1.get_json()["artwork_id"]

    # Update artwork
    update_data = {"price": 75.0}
    r2 = client.put(f"/artist/artwork/{artwork_id}", headers={"Authorization": f"Bearer {token}"}, json=update_data)
    assert r2.status_code == 200
    assert r2.get_json()["success"] is True

    # Delete artwork
    r3 = client.delete(f"/artist/artwork/{artwork_id}", headers={"Authorization": f"Bearer {token}"})
    assert r3.status_code == 200
    assert r3.get_json()["success"] is True
