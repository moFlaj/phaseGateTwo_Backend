# app/buyer/dto/requests/create_order_request.py
from dataclasses import dataclass
from typing import Optional
from app.shared.exceptions.custom_errors import ValidationError
from app.shared.exceptions.custom_errors import InvalidQuantityError


@dataclass
class CreateOrderRequest:
    artwork_id: str
    quantity: int = 1
    shipping_address: Optional[dict] = None

    def validate(self) -> None:
        if not self.artwork_id or not isinstance(self.artwork_id, str):
            raise ValidationError("artwork_id is required and must be a string.")
        if not isinstance(self.quantity, int) or self.quantity < 1:
            raise InvalidQuantityError("quantity must be an integer >= 1")
