import json
import pytest
from app.shared.utilities.token_manager import TokenManager


# --- Mock S3 implementation --------------------------------------------------
class MockS3:
    """Fake boto3 S3 client for testing signed URL generation."""

    def generate_presigned_url(self, operation_name, params=None, expiresIn=None):
        bucket = params.get("Bucket", "test-bucket")
        key = params.get("Key", "unknown-key")
        return f"https://{bucket}.mock/{operation_name}/{key}?expires={expiresIn}"


# @pytest.fixture(autouse=True)
# def patch_boto3(monkeypatch):
#     """Ensure S3Service never touches AWS during tests."""
#     monkeypatch.setattr("app.artist.services.s3_service.boto3.client",
#                         lambda *a, **kw: MockS3())
#     yield


@pytest.fixture()
def artist_jwt(app):
    return f"Bearer {TokenManager.generate_access_token('artist@example.com', 'artist', app.config['SECRET_KEY'])}"


def post_json(client, url, data, jwt=None):
    headers = {"Content-Type": "application/json"}
    if jwt:
        headers["Authorization"] = jwt
    return client.post(url, data=json.dumps(data), headers=headers)


# --- Tests -------------------------------------------------------------------

def test_generate_upload_url_private_flow(client, artist_jwt):
    """Requesting an upload URL should return both upload_url and key."""
    resp = client.get("/api/artist/works/upload-url?filename=test.jpg",
                      headers={"Authorization": artist_jwt})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "upload_url" in data
    assert "key" in data
    assert data["upload_url"].startswith("https://mock-s3.amazonaws.com/test-bucket/artworks/")


def test_get_artwork_returns_signed_get_url(client, artist_jwt, clear_test_db):
    """
    After artwork creation, retrieving the artwork should replace s3_key
    with a signed temporary image_url.
    """
    # 1) Create new artwork
    create_resp = post_json(client, "/api/artist/works",
                            {"title": "MockedArt", "price": 250.0,
                             "s3_key": "artworks/test_private.jpg"},
                            jwt=artist_jwt)
    assert create_resp.status_code == 201
    art_id = create_resp.get_json()["artwork_id"]

    # 2) Fetch artwork (should have signed image_url)
    get_resp = client.get(f"/api/artist/works/{art_id}",
                          headers={"Authorization": artist_jwt})
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert "image_url" in data
    assert data["image_url"].startswith("https://mock-s3.amazonaws.com/test-bucket/artworks/")
    # Note: The global mock doesn't include expires parameter in URL
