# app/buyer/dtos/responses/cart_response.py
from dataclasses import dataclass, asdict

@dataclass
class CartResponse:
    success: bool
    message: str
    cart_id: str = None
    total_amount: float = 0.0

    def to_dict(self):
        return asdict(self)
