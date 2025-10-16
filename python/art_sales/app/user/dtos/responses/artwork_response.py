# app/artist/dto/responses/artwork_response.py
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ArtworkResponse:
    success: bool
    message: str
    artwork_id: Optional[str] = None
    artwork: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)
