#app/models/user_model
from dataclasses import dataclass, field, asdict
from typing import Optional
from bson import ObjectId

@dataclass
class User:
    _id: Optional[ObjectId] = field(default=None)
    name: str = ""
    email: str = ""
    password: str = ""
    role: str = ""  # 'artist' or 'buyer'

    def to_dict(self):
        data = asdict(self)
        # Convert _id to ObjectId if it's a string
        if data["_id"] and isinstance(data["_id"], str):
            data["_id"] = ObjectId(data["_id"])
        # Remove _id if None, so MongoDB will auto-generate it
        if data["_id"] is None:
            data.pop("_id")
        return data
