# app/buyer/dtos/requests/add_to_cart_request.py
from dataclasses import dataclass
from app.shared.exceptions.custom_errors import ValidationError

@dataclass
class AddToCartRequest:
    artwork_id: str
    quantity: int = 1

    def validate(self):
        if not self.artwork_id:
            raise ValidationError("Artwork ID is required.")
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
