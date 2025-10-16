from typing import Any
from flask import Blueprint, request, jsonify, current_app
from app.auth.domain.user_signup_request import UserSignupRequest
from app.auth.domain.user_login_request import UserLoginRequest
from app.auth.domain.user_signup_response import UserSignupResponse
from app.auth.domain.user_login_response import UserLoginResponse
from app.auth.persistence.user_repository import UserRepository
from app.auth.persistence.verification_repository import VerificationRepository
from app.shared.utilities.password_hasher import PasswordHasher
from app.auth.services.verification_service import VerificationService
from app.auth.services.auth_services import AuthService
from app.shared.exceptions.custom_errors import VerificationNotFoundError, UserAlreadyExistsError, InvalidVerificationCodeError
from typing import Any

email_service: Any = None

auth_service: AuthService | None = None
user_repository = UserRepository()
password_hasher = PasswordHasher()
verification_repository = VerificationRepository()
verification_service = VerificationService(verification_repository,
                                           password_hasher)
# Remove the url_prefix from here since it's set in app_runner.py
auth_bp = Blueprint("auth", __name__)


def init_services(email_service_instance, async_email: bool = False) -> None:
    global email_service, auth_service
    email_service = email_service_instance
    current_app.config["EMAIL_SERVICE"] = email_service
    auth_service = AuthService(
        repo=user_repository,
        password_hasher=password_hasher,
        verification_service=verification_service,
        email_service=email_service,
        async_email=async_email,
    )


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)
    req = UserSignupRequest(**data)
    req.validate()
    try:
        response: UserSignupResponse = auth_service.signup_user(req)
        return jsonify(response.__dict__), 202 if response.success else 400
    except UserAlreadyExistsError as e:
        return jsonify({"success": False, "message": str(e)}), 409
    except Exception as e:
        # Check if it's a UserAlreadyExistsError (in case it's wrapped)
        if "User with this email already exists" in str(e):
            return jsonify({"success": False, "message": str(e)}), 409
        raise


@auth_bp.route("/verify", methods=["POST"])
def verify_signup():
    data = request.get_json(force=True)
    email = data.get("email")
    code = data.get("code")
    if not email or not code:
        return jsonify({"success": False, "message": "Email and code are required."}), 400
    signup_request = UserSignupRequest(
            name=data.get("name", ""),
            email=email,
            password=data.get("password", ""),
            role=data.get("role", "")
        )
    try:
        response: UserSignupResponse = auth_service.verify_and_create_user(email, code, signup_request)
        return jsonify(response.__dict__), 201 if response.success else 400
    except VerificationNotFoundError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except UserAlreadyExistsError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except InvalidVerificationCodeError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        # Check if it's a VerificationNotFoundError (in case it's wrapped)
        if "No verification record found for this email" in str(e):
            return jsonify({"success": False, "message": str(e)}), 404
        # Check if it's an InvalidVerificationCodeError (in case it's wrapped)
        if "Invalid verification code" in str(e):
            return jsonify({"success": False, "message": str(e)}), 400
        raise


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    req = UserLoginRequest(**data)
    req.validate()
    response: UserLoginResponse = auth_service.login_user(req)
    return jsonify(response.__dict__), 200 if response.success else 401