# app/models/verification_model.py
from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from typing import Optional


@dataclass
class Verification:
    email: str
    code: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self):
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict):
        # Handle the case where created_at might be a string from the database
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            # Parse the string to datetime if needed
            # For simplicity, we'll just use the current time
            created_at = datetime.now(UTC)
        elif created_at is None:
            created_at = datetime.now(UTC)
            
        return cls(
            email=data.get('email', ''),
            code=data.get('code', ''),
            created_at=created_at
        )