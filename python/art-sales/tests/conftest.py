# app/tests/conftest.py
import pytest
from app.app_runner import create_app, mongo
from app.config.db_config import TestConfig


@pytest.fixture(scope="session")
def app():
    """
    Creates a Flask app instance with test configuration.
    """
    app = create_app(config_class=TestConfig)
    return app


@pytest.fixture(autouse=True)
def clean_db(app):
    """
    Automatically drops the test database before each test.
    """
    with app.app_context():
        mongo.cx.drop_database(TestConfig.DB_NAME)
    yield
    # optional: clean up again after test
    with app.app_context():
        mongo.cx.drop_database(TestConfig.DB_NAME)


@pytest.fixture
def client(app):
    """
    Provides a Flask test client for sending requests to the app.
    """
    return app.test_client()
