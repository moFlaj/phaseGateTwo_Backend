# tests/integration/test_artist_flow.py
import json
import pytest
from bson import ObjectId
from app.shared.utilities.token_manager import TokenManager
from flask import current_app
from app.extensions import mongo


@pytest.fixture(scope="function")
def clear_artworks_collection(app):
    """Ensure a clean artworks collection before and after each test."""
    db_name = app.config["DB_NAME"]
    coll = mongo.cx[db_name]["artworks"]
    coll.delete_many({})
    yield
    coll.delete_many({})


@pytest.fixture(scope="function")
def artist_jwt(app):
    """Generate a JWT for test artist user."""
    secret = app.config["SECRET_KEY"]
    token = TokenManager.generate_access_token(
        user_id="artist@example.com",
        role="artist",
        secret=secret,
        expires_hours=1,
    )
    return f"Bearer {token}"


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


def put_json(client, url, data, jwt=None):
    headers = {"Content-Type": "application/json"}
    if jwt:
        headers["Authorization"] = jwt
    return client.put(url, data=json.dumps(data), headers=headers)


def delete_json(client, url, jwt=None):
    headers = {"Authorization": jwt} if jwt else {}
    return client.delete(url, headers=headers)


# ---------- TEST CASES ---------- #

def test_dashboard_summary(client, artist_jwt, clear_artworks_collection):
    resp = get_json(client, "/api/artist/dashboard", jwt=artist_jwt)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["success"] is True
    assert "summary" in data
    assert "total_artworks" in data["summary"]


def test_create_and_list_artworks(client, artist_jwt, clear_artworks_collection):
    payload = {
        "title": "Sunset Canvas",
        "price": 150.0,
        "medium": "Acrylic",
        "dimensions": "20x30 cm",
        "description": "Warm orange sunset scene.",
        "is_original": True
    }
    # Create artwork
    resp = post_json(client, "/api/artist/works", payload, jwt=artist_jwt)
    data = resp.get_json()
    assert resp.status_code == 201
    assert data["success"] is True
    art_id = data["artwork_id"]
    assert ObjectId.is_valid(art_id)

    # List artworks
    resp = get_json(client, "/api/artist/works", jwt=artist_jwt)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["success"] is True
    assert isinstance(data["artworks"], list)
    assert len(data["artworks"]) == 1
    assert data["artworks"][0]["title"] == "Sunset Canvas"


def test_get_and_update_artwork(client, artist_jwt, clear_artworks_collection):
    # Create first
    create_resp = post_json(
        client,
        "/api/artist/works",
        {"title": "Blue Sky", "price": 120.0},
        jwt=artist_jwt
    )
    art_id = create_resp.get_json()["artwork_id"]

    # Get single artwork
    resp = get_json(client, f"/api/artist/works/{art_id}", jwt=artist_jwt)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["title"] == "Blue Sky"

    # Update artwork
    resp = put_json(client, f"/api/artist/works/{art_id}", {"price": 180.0}, jwt=artist_jwt)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["message"] == "Artwork updated successfully"


def test_delete_artwork(client, artist_jwt, clear_artworks_collection):
    create_resp = post_json(
        client,
        "/api/artist/works",
        {"title": "To Delete", "price": 50.0},
        jwt=artist_jwt
    )
    art_id = create_resp.get_json()["artwork_id"]

    resp = delete_json(client, f"/api/artist/works/{art_id}", jwt=artist_jwt)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["message"] == "Artwork deleted successfully"

    # Verify not found
    resp = get_json(client, f"/api/artist/works/{art_id}", jwt=artist_jwt)
    assert resp.status_code == 404


def test_generate_upload_url(monkeypatch, client, artist_jwt, clear_artworks_collection):
    """Ensure presigned URL generation returns expected structure."""

    class MockS3:
        def generate_presigned_url(self, *_args, **_kwargs):
            return "https://mock-s3-url"

    monkeypatch.setattr("app.user.services.s3_service.boto3.client", lambda *_a, **_kw: MockS3())
    resp = client.get("/api/artist/works/upload-url?filename=test.jpg",
                      headers={"Authorization": artist_jwt})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["success"] is True
    assert "upload_url" in data
    assert "final_url" in data


def test_list_artworks_includes_presigned_urls(client, app, artist_jwt, seed_mongo_data):
    """Artist list should include signed image URLs for artworks with s3_key."""
    resp = client.get("/api/artist/works", headers={"Authorization": artist_jwt})
    assert resp.status_code == 200
    data = resp.get_json()
    artworks = data["artworks"]

    # Ensure seeded data returned
    assert len(artworks) == 2

    # The artwork with an s3_key should have an image_url
    art_with_url = [a for a in artworks if a.get("s3_key")]
    for art in art_with_url:
        assert "image_url" in art
        assert art["image_url"].startswith("https://mock-s3.amazonaws.com/")


def test_list_artworks_pagination(client, app, artist_jwt, seed_mongo_data):
    """Pagination should limit results and respect skip."""
    resp = client.get("/api/artist/works?limit=1&skip=0", headers={"Authorization": artist_jwt})
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data["artworks"]) == 1


def test_get_single_artwork_returns_signed_url(client, app, artist_jwt, seed_mongo_data):
    resp = client.get("/api/artist/works/507f1f77bcf86cd799439011", headers={"Authorization": artist_jwt})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "image_url" in data
    assert "mock-s3.amazonaws.com" in data["image_url"]
