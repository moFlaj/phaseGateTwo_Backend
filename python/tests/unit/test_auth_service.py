import pytest
from unittest.mock import MagicMock
from datetime import datetime

from app.auth.services.auth_services import AuthService
from app.auth.domain.user_signup_request import UserSignupRequest
from app.auth.domain.user_login_request import UserLoginRequest
from app.auth.domain.user_signup_response import UserSignupResponse
from app.auth.domain.user_model import User
from app.auth.domain.verification_model import Verification
from app.shared.exceptions.custom_errors import (
    UserAlreadyExistsError,
    InvalidVerificationCodeError,
    ValidationError,
)


def test_sign_up_user_creates_verification(auth_service, mock_dependencies, app):
    """Should create a new verification for a non-existent user and send an email."""
    req = UserSignupRequest(
        name="Alice",
        email="alice@example.com",
        password="StrongPass123",
        role="buyer",
    )

    mock_dependencies["repo"].find_by_email.return_value = None
    mock_dependencies["verification_service"].create_verification_for.return_value = Verification(
        email=req.email, code="123456"
    )

    with app.app_context():
        response = auth_service.signup_user(req)

    mock_dependencies["verification_service"].create_verification_for.assert_called_once_with(req)
    mock_dependencies["email_service"].send_verification_email.assert_called_once_with(req.email,
                    "http://localhost:3000/verify?email=alice@example.com & code = 123456")

    assert isinstance(response, UserSignupResponse)
    assert response.success is True
    assert "Verification" in response.message


def test_sign_up_user_duplicate_email(auth_service, mock_dependencies):
    """Should raise if a user with the same email already exists."""
    req = UserSignupRequest("Alice", "alice@example.com", "StrongPass123", "buyer")
    mock_dependencies["repo"].find_by_email.return_value = {"email": req.email}

    with pytest.raises(UserAlreadyExistsError):
        auth_service.signup_user(req)


def test_verify_and_create_user_success(auth_service, mock_dependencies):
    """Should create user when verification code matches."""
    req = UserSignupRequest("Alice", "alice@example.com", "StrongPass123", "buyer")
    verification = Verification(email=req.email, code="654321")

    mock_dependencies["verification_service"].verification_repo.find_by_email.return_value = verification.to_dict()
    mock_dependencies["password_hasher"].hash_password.return_value = "hashed123"
    mock_dependencies["repo"].insert_user.return_value = "user123"
    # Add this line to fix the test - mock that no user exists yet
    mock_dependencies["repo"].find_by_email.return_value = None

    response = auth_service.verify_and_create_user(req.email, "654321", req)

    mock_dependencies["repo"].insert_user.assert_called_once()
    mock_dependencies["verification_service"].delete_verification.assert_called_once_with(req.email)
    assert isinstance(response, UserSignupResponse)
    assert response.success is True


def test_verify_and_create_user_invalid_code(auth_service, mock_dependencies):
    """Should raise when provided code does not match stored verification."""
    req = UserSignupRequest("Alice", "alice@example.com", "StrongPass123", "buyer")
    stored_verification = Verification(email=req.email, code="111111")

    mock_dependencies["verification_service"].verification_repo.find_by_email.return_value = stored_verification.to_dict()

    with pytest.raises(ValidationError):
        auth_service.verify_and_create_user(req.email, "999999", req)


def test_login_success(auth_service, mock_dependencies):
    """Should return JWT when valid credentials are provided."""
    req = UserLoginRequest("alice@example.com", "StrongPass123")
    user = User(email=req.email, password="hashed123", name="Alice", role="buyer")

    mock_dependencies["repo"].find_by_email.return_value = user.to_dict()
    mock_dependencies["password_hasher"].check_password.return_value = True
    auth_service._generate_token = MagicMock(return_value="jwt-token")

    response = auth_service.login_user(req)

    assert response.success is True
    assert response.__getattribute__("access_token") == "jwt-token"
    mock_dependencies["repo"].find_by_email.assert_called_once_with(req.email)


# def test_login_invalid_password(auth_service, mock_dependencies):
#     """Should raise InvalidCredentialsError when password is wrong."""
#     req = UserLoginRequest("alice@example.com", "wrongpass")
#     user = User(email=req.email, password="hashed123", name="Alice", role="buyer")
#
#     mock_dependencies["repo"].find_by_email.return_value = user
#     mock_dependencies["password_hasher"].check_password.return_value = False
#
#     with pytest.raises(InvalidCredentialsError):
#         auth_service.login_user(req)
