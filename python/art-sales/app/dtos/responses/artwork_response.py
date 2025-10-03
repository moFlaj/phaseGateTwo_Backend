# app/dtos/responses/artwork_response.py
from dataclasses import dataclass

@dataclass
class ArtworkResponse:
    success: bool
    message: str
    artwork_id: str = None
