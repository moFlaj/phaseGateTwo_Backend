# app/dtos/requests/buyer_update_profile_request.py
from dataclasses import dataclass

@dataclass
class BuyerUpdateProfileRequest:
    name: str = None
    email: str = None
    password: str = None

    def validate(self):
        if not (self.name or self.email or self.password):
            raise ValueError("At least one field must be provided")
        if self.password and len(self.password) < 6:
            raise ValueError("Password must be at least 6 characters")
