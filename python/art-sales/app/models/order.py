from dataclasses import dataclass, field, asdict
from typing import Optional
from bson import ObjectId
from datetime import datetime

@dataclass
class Order:
    _id: Optional[ObjectId] = field(default=None)
    buyer_id: str = ""
    items: list = field(default_factory=list)  # list of product dicts
    total_amount: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        data = asdict(self)
        if data["_id"] and isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
        if data["_id"] is None:
            data.pop("_id")
        return data
