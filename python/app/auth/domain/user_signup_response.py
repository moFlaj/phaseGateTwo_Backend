from dataclasses import dataclass
from typing import Optional

@dataclass
class UserSignupResponse:
    success: bool
    message: str
    user_id: Optional[str] = None
