import pytest
from app.auth.services.auth_services import AuthService
from tests.utils.mock_factory import make_auth_mocks


@pytest.fixture(scope="function")
def mock_dependencies():
    """Provide dependency mocks for AuthService (aligned with current constructor)."""
    mocks = make_auth_mocks()
    mocks["verification_service"] = mocks.pop("verification_repo")
    mocks["repo"] = mocks.pop("user_repo")

    return mocks


@pytest.fixture(scope="function")
def auth_service(mock_dependencies):
    """Create AuthService with dependency mocks."""
    return AuthService(
        repo=mock_dependencies["repo"],
        password_hasher=mock_dependencies["password_hasher"],
        verification_service=mock_dependencies["verification_service"],
        email_service=mock_dependencies["email_service"],
        async_email=False,
    )
