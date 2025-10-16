# app/dtos/requests/user_login_request.py
from dataclasses import dataclass
from app.shared.exceptions.custom_errors import ValidationError


@dataclass
class UserLoginRequest:
    email: str
    password: str

    def validate(self) -> None:
        if not self.email:
            raise ValidationError("Email is required")
        if not self.password:
            raise ValidationError("Password is required")
