from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from typing import Optional, Dict

@dataclass
class Artwork:
    title: str
    price: float
    medium: Optional[str] = None
    dimensions: Optional[str] = None
    description: Optional[str] = None
    is_original: bool = True
    variants: Optional[Dict] = field(default_factory=dict)
    artist_id: Optional[str] = None
    s3_key: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self):
        return asdict(self)
