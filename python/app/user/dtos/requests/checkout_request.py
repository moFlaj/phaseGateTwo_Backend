# app/buyer/dtos/requests/checkout_request.py
from dataclasses import dataclass
from app.shared.exceptions.custom_errors import ValidationError

@dataclass
class CheckoutRequest:
    cart_id: str

    def validate(self):
        if not self.cart_id:
            raise ValidationError("Cart ID required.")