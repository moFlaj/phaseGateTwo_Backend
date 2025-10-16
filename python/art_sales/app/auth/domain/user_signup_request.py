from dataclasses import dataclass
from typing import Optional
from app.shared.exceptions.custom_errors import ValidationError
import re

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

class UserSignupRequest:
    def __init__(self, name: str, email: str, password: str, role: str):
        self.name = name.strip() if name else None
        self.email = email.strip().lower() if email else None
        self.password = password
        self.role = role
        self.validate()

    def validate(self):
        if not self.name:
            raise ValidationError("Name is required")

        if not self.email:
            raise ValidationError("Email is required")

        if not EMAIL_REGEX.match(self.email):
            raise ValidationError("Invalid email format")

        if not self.password or len(self.password) < 8:
            raise ValidationError("Password must be at least 8 characters")

        if self.role not in ["buyer", "artist"]:
            raise ValidationError("Role must be 'buyer' or 'artist'")
