# app/dtos/requests/user_login_request.py
from dataclasses import dataclass

@dataclass
class UserLoginRequest:
    email: str
    password: str

    def validate(self):
        if not self.email or not self.password:
            raise ValueError("Email and password are required.")
