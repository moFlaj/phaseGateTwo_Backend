# app/tests/conftest.py
import pytest
from app.app_runner import create_app, mongo
from app.config.db_config import TestConfig

@pytest.fixture(scope = "session")
def app():
    """
    Creates a Flask app instance with test configuration.
    Cleans relevant collections before each test run.
    """
    app = create_app(config_class=TestConfig)

    with app.app_context():
        db = mongo.cx[TestConfig.DB_NAME]
        # Clean users and orders collections
        db.users.delete_many({})
        db.orders.delete_many({})

    yield app

@pytest.fixture
def client(app):
    """
    Provides a Flask test client for sending requests to the app.
    """
    return app.test_client()
