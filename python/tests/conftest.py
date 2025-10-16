# tests/conftest.py
import pytest
import os
from bson import ObjectId
from flask import Flask
from app.app_runner import create_app
from app.extensions import mongo


@pytest.fixture(scope="session")
def app() -> Flask:
    """
    Create a Flask test app using TestConfig.
    The app_runner automatically injects MockMailer via TestConfig.USE_MOCK_MAILER=True.
    """
    os.environ["FLASK_ENV"] = "testing"
    os.environ["USE_MOCK_MAILER"] = "True"
    os.environ["USE_MOCK_STRIPE"] = "True"
    os.environ["STRIPE_SECRET_KEY"] = "sk_test_mock123"
    os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_mock123"
    os.environ["PAYSTACK_SECRET_KEY"] = "sk_test_mock123"
    os.environ["DB_NAME"] = "art_sales_test"

    app = create_app("app.shared.config.db_config.TestConfig")
    return app


@pytest.fixture(scope="session")
def client(app):
    """Provide a test client."""
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def clear_test_db(app):
    """Ensure MongoDB is empty before and after each test."""
    with app.app_context():
        db = mongo.cx[app.config["DB_NAME"]]
        for coll in db.list_collection_names():
            db[coll].delete_many({})
        yield
        for coll in db.list_collection_names():
            db[coll].delete_many({})


@pytest.fixture(scope="function")
def seed_mongo_data(app):
    """Seed MongoDB with mock artist, artworks, and orders for each test."""
    with app.app_context():
        db = mongo.cx[app.config["DB_NAME"]]
        # Clear existing data first
        for coll in db.list_collection_names():
            db[coll].delete_many({})
        
        artworks = [
            {
                "_id": ObjectId("507f1f77bcf86cd799439011"),
                "artist_id": "artist@example.com",
                "title": "Sunset Painting",
                "price": 200.0,
                "medium": "Oil",
                "dimensions": "30x40",
                "s3_key": "artworks/a1.jpg",
            },
            {
                "_id": ObjectId("507f1f77bcf86cd799439012"),
                "artist_id": "artist@example.com",
                "title": "Abstract Sculpture",
                "price": 450.0,
                "medium": "Marble",
                "dimensions": "20x20",
            },
        ]

        orders = [
            {
                "_id": "o1",
                "buyer_id": "buyer@example.com",
                "artist_id": "artist@example.com",
                "artwork_id": "507f1f77bcf86cd799439011",
                "price": 200.0,
                "quantity": 1,
                "status": "completed",
            }
        ]

        db["artworks"].insert_many(artworks)
        db["orders"].insert_many(orders)
        yield db


@pytest.fixture(scope="function", autouse=True)
def mock_s3(monkeypatch):
    """Prevent AWS network calls by mocking boto3 client globally."""
    class MockS3:
        def generate_presigned_url(self, operation_name, Params=None, ExpiresIn=None):
            return f"https://mock-s3.amazonaws.com/{Params['Bucket']}/{Params['Key']}"

    monkeypatch.setattr("app.user.services.s3_service.boto3.client", lambda *_a, **_kw: MockS3())


@pytest.fixture(scope="function")
def mock_mailer(app):
    """
    Retrieve the mailer injected by app_runner (MockMailer in TestConfig).
    This allows inspecting sent emails in tests.
    """
    return app.config.get("EMAIL_SERVICE")


@pytest.fixture(scope="function", autouse=True)
def mock_paystack(monkeypatch):
    """Mock Paystack API calls to prevent network requests during testing."""
    import json
    
    # Store reference to cart mapping
    reference_cart_map = {}
    
    def mock_post(*args, **kwargs):
        print("DEBUG: mock_post called with args:", args, "kwargs:", kwargs)
        class MockResponse:
            def __init__(self, json_data, status_code=200):
                self.json_data = json_data
                self.status_code = status_code
            
            def json(self):
                return self.json_data
                
            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception(f"HTTP {self.status_code}")
        
        url = args[0] if args else kwargs.get('url', '')
        print("DEBUG: mock_post called for URL:", url)
        
        if 'transaction/initialize' in url:
            # Extract the reference from the request payload
            json_data = kwargs.get('json', {})
            reference = json_data.get('reference', 'mock_reference_456')
            cart_id = json_data.get('metadata', {}).get('cart_id')
            # Store the mapping
            if cart_id:
                reference_cart_map[reference] = cart_id
            print("DEBUG: Returning mock response for transaction/initialize with reference:", reference)
            return MockResponse({
                "status": True,
                "message": "Authorization URL created",
                "data": {
                    "authorization_url": "https://checkout.paystack.co/mock_payment_page",
                    "access_code": "mock_access_code_123",
                    "reference": reference
                }
            })
        elif 'transferrecipient' in url:
            return MockResponse({
                "status": True,
                "message": "Recipient created",
                "data": {
                    "recipient_code": "mock_recipient_code_123",
                    "type": "nuban",
                    "name": "Mock Recipient",
                    "account_number": "0123456789",
                    "bank_code": "057",
                    "currency": "NGN"
                }
            })
        elif 'transfer' in url:
            return MockResponse({
                "status": True,
                "message": "Transfer initiated",
                "data": {
                    "transfer_code": "mock_transfer_code_123",
                    "status": "pending",
                    "reference": "mock_transfer_reference_456"
                }
            })
        
        print("DEBUG: Returning 404 for URL:", url)
        return MockResponse({"status": False, "message": "Not found"}, 404)
    
    def mock_get(*args, **kwargs):
        print("DEBUG: mock_get called with args:", args, "kwargs:", kwargs)
        class MockResponse:
            def __init__(self, json_data, status_code=200):
                self.json_data = json_data
                self.status_code = status_code
            
            def json(self):
                return self.json_data
                
            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception(f"HTTP {self.status_code}")
        
        url = args[0] if args else kwargs.get('url', '')
        print("DEBUG: mock_get called for URL:", url)
        
        if 'transaction/verify' in url:
            # Extract the reference from the URL
            import re
            match = re.search(r'/transaction/verify/([^/]+)', url)
            reference = match.group(1) if match else "mock_reference_456"
            # Get the cart ID from the mapping
            cart_id = reference_cart_map.get(reference)
            print("DEBUG: Returning mock response for transaction/verify with reference:", reference, "cart_id:", cart_id)
            return MockResponse({
                "status": True,
                "message": "Verification successful",
                "data": {
                    "status": "success",
                    "reference": reference,
                    "amount": 10000,
                    "customer": {
                        "email": "customer@example.com"
                    },
                    "metadata": {
                        "cart_id": cart_id
                    }
                }
            })
        
        print("DEBUG: Returning 404 for URL:", url)
        return MockResponse({"status": False, "message": "Not found"}, 404)
    
    # Mock both POST and GET requests
    print("DEBUG: Applying mock_paystack fixture")
    monkeypatch.setattr("requests.post", mock_post)
    monkeypatch.setattr("requests.get", mock_get)
    print("DEBUG: mock_paystack fixture applied")
    return "mock_paystack_applied"
