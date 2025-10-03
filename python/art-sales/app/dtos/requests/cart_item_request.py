# app/dtos/requests/cart_item_request.py
from dataclasses import dataclass

@dataclass
class CartItemRequest:
    artwork_id: str
    quantity: int = 1

    def validate(self):
        if not self.artwork_id:
            raise ValueError("Artwork ID is required")
        if not isinstance(self.quantity, int) or self.quantity <= 0:
            raise ValueError("Quantity must be positive")
