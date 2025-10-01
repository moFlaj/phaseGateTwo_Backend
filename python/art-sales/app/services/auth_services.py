from flask import current_app

from app.dtos.requests.user_login_request import UserLoginRequest
from app.dtos.requests.user_signup_request import UserSignupRequest
from app.dtos.responses.user_login_response import UserLoginResponse

from app.dtos.responses.user_signup_response import UserSignupResponse

from app.exceptions.custom_exceptions import (
    ValidationException,
    ResourceExistsException
)
from app.mappers.user_mapper import UserMapper
from app.persistence.user_repository import UserRepository
from app.utilities.password_hasher import PasswordHasher
from app.utilities.token_manager import TokenManager
from app.validators.user_validator import UserValidator


class AuthService:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasher):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    # ---------- SIGNUP ----------
    def signup_user(self, request_dto: UserSignupRequest) -> UserSignupResponse:
        try:
            UserValidator.validate_signup(request_dto)
        except ValueError as ve:
            raise ValidationException(str(ve))

        if self.user_repository.find_by_email(request_dto.email):
            raise ResourceExistsException("Email already in use.")

        hashed_pw = self.password_hasher.hash_password(request_dto.password)
        user = UserMapper.dto_to_model(request_dto, hashed_pw)
        inserted_id = self.user_repository.insert_user(user)

        return UserSignupResponse(
            success=True,
            message="Account created successfully.",
            user_id=str(inserted_id)
        )

    # ---------- LOGIN ----------
    def login_user(self, request_dto: UserLoginRequest) -> UserLoginResponse:
        try:
            request_dto.validate()
        except ValueError as ve:
            raise ValidationException(str(ve))

        user = self.user_repository.find_by_email(request_dto.email)
        if not user:
            return self._failed_login_response()

        if not self.password_hasher.verify_password(request_dto.password, user["password"]):
            return self._failed_login_response()

        token = self._generate_token(user)

        return UserLoginResponse(
            success=True,
            message="Login successful",
            access_token=token,
            user_id=str(user["_id"]),
            role=user.get("role")
        )

    # ---------- PRIVATE HELPERS ----------
    def _failed_login_response(self) -> UserLoginResponse:
        """Return a generic failure response (avoid leaking email existence)."""
        return UserLoginResponse(
            success=False,
            message="Invalid email or password"
        )

    def _generate_token(self, user: dict) -> str:
        secret = current_app.config["SECRET_KEY"]
        expires = current_app.config.get("JWT_EXP_HOURS", 1)
        return TokenManager.generate_access_token(
            str(user["_id"]),
            user.get("role", ""),
            secret,
            expires
        )
