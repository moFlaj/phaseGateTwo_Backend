# app/auth/services/auth_services.py
from flask import current_app
from app.auth.persistence.user_repository import UserRepository
from app.shared.utilities.password_hasher import PasswordHasher
from app.shared.utilities.token_manager import TokenManager
from app.auth.services.verification_service import VerificationService
from app.shared.utilities.email_service import EmailService
from app.auth.domain.user_signup_request import UserSignupRequest
from app.auth.domain.user_login_request import UserLoginRequest
from app.auth.domain.user_signup_response import UserSignupResponse
from app.auth.domain.user_login_response import UserLoginResponse
from app.shared.exceptions.custom_errors import (
    ValidationError,
    UserAlreadyExistsError,
    VerificationNotFoundError,
)
from app.shared.jobs.email_jobs import enqueue_email_job
from app.auth.mappers.user_mapper import UserMapper
from flask import current_app


class AuthService:
    def __init__(
            self,
            repo: UserRepository,
            password_hasher: PasswordHasher,
            verification_service: VerificationService,
            email_service: EmailService,
            async_email: bool = False,
    ) -> None:
        self.repo = repo
        self.password_hasher = password_hasher
        self.verification_service = verification_service
        self.email_service = email_service
        self.async_email = async_email

    def signup_user(self, req: UserSignupRequest) -> UserSignupResponse:
        if self.repo.find_by_email(req.email):
            raise UserAlreadyExistsError("User with this email already exists")
        verification = self.verification_service.create_verification_for(req)
        frontend_verify_url = current_app.config.get("FRONTEND_VERIFY_URL",
                                                     "http://localhost:3000/verify")
        verification_link = f"{frontend_verify_url}?email={req.email} & code = {verification.code}"
        if self.async_email:
            enqueue_email_job(req.email, verification_link)
        else:
            self.email_service.send_verification_email(req.email, verification_link)
        return UserSignupResponse(success=True, message="Verification email sent.")

    def verify_and_create_user(self, email: str, code: str, req:UserSignupRequest) -> UserSignupResponse:
        record = self.verification_service.verification_repo.find_by_email(email)
        if not record:
            raise VerificationNotFoundError("No verification record found for this email")
        if record.get("code") != code:
            raise ValidationError("Invalid verification code")
        
        # Check if user already exists (in case of double verification attempt)
        existing_user = self.repo.find_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError("User already verified and created")
            
        hashed_pw = self.password_hasher.hash_password(req.password)
        new_user = UserMapper.dto_to_model(req, hashed_pw)
        user_id = self.repo.insert_user(new_user)
        self.verification_service.delete_verification(email)
        
        # Create wallet for the new user
        try:
            from app.wallet.controllers.wallet_controller import wallet_service
            if wallet_service:
                wallet_service.create_wallet(str(user_id))
        except Exception as e:
            # Log the error but don't fail user creation
            print(f"Warning: Failed to create wallet for user {user_id}: {e}")
        
        return UserSignupResponse(success=True, message="User created successfully", user_id=str(user_id))


    def login_user(self, req: UserLoginRequest) -> UserLoginResponse:
        user = self.repo.find_by_email(req.email)
        if not user:
            return UserLoginResponse(success=False, message="Email not registered. Sign up first.")

        if not self.password_hasher.verify_password(req.password, user.get("password")):
            return UserLoginResponse(success=False, message="Invalid password")
        token = self._generate_token(user)
        return UserLoginResponse(success=True, message="Login successful",
                                 access_token=token, user_id=str(user.get("_id")), role=user.get("role"))

    def _generate_token(self, user: dict) -> str:
        secret = current_app.config.get("SECRET_KEY", "dev-secret")
        expires = int(current_app.config.get("JWT_EXP_HOURS", 1))
        return TokenManager.generate_access_token(str(user.get("_id")),
                                                      user.get("role", ""), secret, expires)