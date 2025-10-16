from app.user.domain.artwork_model import Artwork
from app.user.dtos.requests.artwork_request import ArtworkRequest

class Mapper:
    @staticmethod
    def from_request(req: ArtworkRequest, artist_id: str) -> Artwork:
        return Artwork(
            title=req.title.strip(),
            price=float(req.price),
            medium=req.medium,
            dimensions=req.dimensions,
            description=req.description,
            is_original=bool(req.is_original),
            variants=req.variants or {},
            artist_id=artist_id,
            s3_key=req.s3_key,
        )
