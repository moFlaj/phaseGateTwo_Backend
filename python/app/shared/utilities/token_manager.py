# app/utilities/token_manager.py
from datetime import datetime, timedelta, UTC
import jwt
from typing import Any

class TokenManager:
    """Encapsulates JWT creation/decoding so AuthService doesn't need to know JWT details."""

    @staticmethod
    def generate_access_token(user_id: str, role: str, secret: str, expires_hours: int = 1) -> str:
        # Build the minimal payload: user id, role, and expiry.
        payload = {
            "user_id": str(user_id),
            "role": role,
            "exp": datetime.now(UTC) + timedelta(hours=expires_hours)
        }
        return jwt.encode(payload, secret, algorithm="HS256")


    @staticmethod
    def decode_token(token: str, secret: str) -> dict[str, Any]:
        # This will raise jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure,
        # which higher layers (decorators / routes) can catch.
        return jwt.decode(token, secret, algorithms=["HS256"])