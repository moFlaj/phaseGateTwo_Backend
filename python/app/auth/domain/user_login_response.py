# app/dtos/responses/user_login_response.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class UserLoginResponse:
    success: bool
    message: str
    access_token: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
