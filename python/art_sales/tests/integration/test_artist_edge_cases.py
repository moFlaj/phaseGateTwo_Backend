# tests/integration/test_artist_edge_cases.py
import json
import pytest
from app.shared.utilities.token_manager import TokenManager
from app.extensions import mongo

@pytest.fixture(scope="function")
def artist_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('artist@example.com', 'artist', app.config['SECRET_KEY'])}"

@pytest.fixture(autouse=True)
def clear_collections(app):
    db = mongo.cx[app.config['DB_NAME']]
    db['artworks'].delete_many({})
    yield
    db['artworks'].delete_many({})

def post_json(client, url, data, jwt=None):
    headers = {"Content-Type": "application/json"}
    if jwt:
        headers["Authorization"] = jwt
    return client.post(url, data=json.dumps(data), headers=headers)

# 1) Missing title -> 400
def test_create_artwork_missing_title(client, artist_jwt):
    payload = {"price": 100.0}
    resp = post_json(client, "/api/artist/works", payload, jwt=artist_jwt)
    assert resp.status_code == 400
    data = resp.get_json()
    assert not data["success"]
    assert "title" in data["message"].lower()

# 2) Negative price -> 400
def test_create_artwork_negative_price(client, artist_jwt):
    payload = {"title": "Bad", "price": -10}
    resp = post_json(client, "/api/artist/works", payload, jwt=artist_jwt)
    assert resp.status_code == 400

# 3) Unauthenticated create -> 401
def test_create_work_unauthenticated(client):
    payload = {"title": "NoAuth", "price": 50}
    resp = client.post("/api/artist/works", json=payload)
    assert resp.status_code == 401

# 4) Forbidden role (buyer trying to create) -> 403
def test_create_work_forbidden_role(client, app):
    # Create buyer token
    token = f"Bearer {TokenManager.generate_access_token('buyer@example.com', 'buyer', app.config['SECRET_KEY'])}"
    payload = {"title": "Forbidden", "price": 60}
    resp = client.post("/api/artist/works", json=payload, headers={"Authorization": token})
    assert resp.status_code == 403

# 5) Get nonexistent artwork -> 404
def test_get_nonexistent_artwork(client, artist_jwt):
    print(artist_jwt)
    resp = client.get("/api/artist/works/507f191e810c19729de860ea", headers={"Authorization": artist_jwt})
    assert resp.status_code == 404

# 6) Update with no fields -> 400
def test_update_artwork_no_updates(client, artist_jwt):
    create = post_json(client, "/api/artist/works", {"title": "Up", "price": 10}, jwt=artist_jwt)
    art_id = create.get_json()["artwork_id"]
    resp = client.put(f"/api/artist/works/{art_id}", json={}, headers={"Authorization": artist_jwt})
    assert resp.status_code == 400

# 7) Delete nonexistent -> 404
def test_delete_nonexistent_artwork(client, artist_jwt):
    resp = client.delete("/api/artist/works/507f191e810c19729de860ea", headers={"Authorization": artist_jwt})
    assert resp.status_code == 404

# 8) Upload-url missing filename -> 400
def test_generate_upload_url_missing_filename(client, artist_jwt):
    resp = client.get("/api/artist/works/upload-url", headers={"Authorization": artist_jwt})
    assert resp.status_code == 400

# 9) Upload-url unauthenticated -> 401
def test_generate_upload_url_unauthenticated(client):
    resp = client.get("/api/artist/works/upload-url")
    assert resp.status_code == 401
