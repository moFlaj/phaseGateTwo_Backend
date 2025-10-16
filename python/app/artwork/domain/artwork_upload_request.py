# app/dtos/requests/artwork_upload_request.py
from dataclasses import dataclass

@dataclass
class ArtworkUploadRequest:
    title: str
    price: float
    image_url: str  # for now, frontend will provide a URL or file path

    def validate(self):
        if not self.title:
            raise ValueError("Artwork title is required")
        if self.price is None or self.price < 0:
            raise ValueError("Artwork price must be non-negative")
        if not self.image_url:
            raise ValueError("Artwork image URL is required")
