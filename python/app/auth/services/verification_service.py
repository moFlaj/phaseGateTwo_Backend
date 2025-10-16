# app/services/verification_service.py
from datetime import datetime, timedelta
import random
import string
from typing import Optional
from app.auth.domain.user_signup_request import UserSignupRequest
from app.auth.domain.verification_model import Verification
from app.auth.persistence.verification_repository import VerificationRepository
from app.shared.utilities.password_hasher import PasswordHasher
from app.shared.exceptions.custom_errors import ValidationError


class VerificationService:
    def __init__(self, verification_repo: VerificationRepository,
                 password_hasher: PasswordHasher) -> None:
        self.verification_repo = verification_repo
        self.password_hasher = password_hasher

    def create_verification_for(self, signup_request: UserSignupRequest) -> Verification:
        """
        Either return existing code if still valid or generate a new one.
        """
        if not signup_request.email:
            raise ValidationError("Email is required for verification")
            
        existing = self.verification_repo.find_by_email(signup_request.email)
        if existing:
            # return same code if not expired
            return Verification.from_dict(existing)

        code = self._generate_code()
        verification = Verification(email=signup_request.email, code=code)
        self.verification_repo.save(verification)
        return verification

    def validate_code(self, email: str, code: str) -> bool:
        row = self.verification_repo.find_by_email(email)
        if not row:
            return False
        return row.get("code") == code

    def hash_password(self, plain_password: str) -> str:
        return self.password_hasher.hash_password(plain_password)

    def delete_verification(self, email: str) -> None:
        self.verification_repo.delete_by_email(email)

    def _generate_code(self, length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))