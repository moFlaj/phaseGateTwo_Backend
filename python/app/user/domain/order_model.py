# app/buyer/models/order.py
from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from typing import Dict, Optional

@dataclass
class Order:
    buyer_id: str
    artist_id: str
    artwork_id: str
    quantity: int
    price: float
    reference: Optional[str] = None         # 🔹 Added for Paystack reference
    status: str = "processing"
    shipping: Optional[Dict] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self):
        return asdict(self)