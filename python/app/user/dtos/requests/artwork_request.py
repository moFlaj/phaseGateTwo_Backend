# app/artist/dto/requests/artwork_request.py
from dataclasses import dataclass
from typing import Optional
from app.shared.exceptions.custom_errors import ValidationError


@dataclass
class ArtworkRequest:
    title: str
    price: float
    medium: Optional[str] = None
    dimensions: Optional[str] = None
    description: Optional[str] = None
    is_original: bool = True
    variants: Optional[dict] = None
    s3_key: Optional[str] = None

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValidationError("Artwork title is required.")
        if not isinstance(self.price, (int, float)) or self.price < 0:
            raise ValidationError("Price must be a non-negative number.")
        if self.variants is not None and not isinstance(self.variants, dict):
            raise ValidationError("Variants must be a dictionary when provided.")
