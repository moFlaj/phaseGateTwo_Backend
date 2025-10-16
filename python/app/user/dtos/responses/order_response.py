# app/buyer/dto/responses/order_response.py
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class OrderResponse:
    success: bool
    message: str
    order_id: Optional[str] = None
    order: Optional[dict] = None

    def to_dict(self):
        return asdict(self)
