# tests/integration/test_buyer_search_flow.py
import json
import pytest
from app.shared.utilities.token_manager import TokenManager

@pytest.fixture
def buyer_auth_header(app):
    token = TokenManager.generate_access_token(user_id="buyer@example.com", role="buyer", secret=app.config["SECRET_KEY"], expires_hours=1)
    return {"Authorization": f"Bearer {token}"}

def test_search_no_filters_returns_results(client, app, buyer_auth_header, seed_mongo_data):
    resp = client.get("/api/buyer/search", headers=buyer_auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["results"], list)
    # seeded test fixture should return at least the artworks we added
    assert len(data["results"]) >= 1

def test_search_text_query_matches_title(client, app, buyer_auth_header, seed_mongo_data):
    # search for "Sunset" which exists in seeded title
    resp = client.get("/api/buyer/search?q=Sunset", headers=buyer_auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert any("Sunset" in a.get("title", "") for a in data["results"])

def test_search_price_range_filters_results(client, app, buyer_auth_header, seed_mongo_data):
    # seed had one artwork at price 200.0 and another at 450.0
    resp = client.get("/api/buyer/search?min_price=100&max_price=300", headers=buyer_auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    for art in data["results"]:
        assert 100 <= float(art["price"]) <= 300

def test_search_invalid_price_range_returns_400(client, app, buyer_auth_header):
    resp = client.get("/api/buyer/search?min_price=1000&max_price=100", headers=buyer_auth_header)
    assert resp.status_code == 400
    data = resp.get_json()
    assert "Invalid price range" in data["message"]

def test_search_pagination_limit_and_skip(client, app, buyer_auth_header, seed_mongo_data):
    # Request only 1 item (limit=1)
    resp = client.get("/api/buyer/search?limit=1&skip=0", headers=buyer_auth_header)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["results"]) == 1
