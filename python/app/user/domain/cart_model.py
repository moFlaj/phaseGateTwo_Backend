# app/buyer/models/cart_model.py
from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from typing import List

@dataclass
class CartItem:
    artwork_id: str
    title: str
    price: float
    quantity: int

@dataclass
class Cart:
    buyer_id: str
    items: List[CartItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def total_amount(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

    def to_dict(self):
        data = asdict(self)
        data["created_at"] = self.created_at
        return data
