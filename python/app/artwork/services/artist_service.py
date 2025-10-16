# app/artist/services/artist_service.py
from bson import ObjectId
from typing import List
from app.artist.persistence.artwork_repository import ArtworkRepository
from app.buyer.persistence.order_repository import OrderRepository
from app.artist.dtos.requests.artwork_request import ArtworkRequest
from app.artist.dtos.responses.artwork_response import ArtworkResponse
from app.artist.mappers.artist_mapper import Mapper
from app.artist.services.s3_service import S3Service
from app.shared.exceptions.custom_errors import (
    ArtworkNotFoundError,
    ValidationError,
)
from app.artist.exceptions.custom_errors import StorageServiceError


class ArtistService:
    def __init__(self, artwork_repo: ArtworkRepository, s3_service: S3Service = None):
        self.artwork_repo = artwork_repo
        self.s3_service = s3_service or S3Service()


    def create_artwork(self, artist_id: str, req: ArtworkRequest) -> ArtworkResponse:
        req.validate()
        model = Mapper.from_request(req, artist_id= artist_id)
        try:
            inserted_id: ObjectId = self.artwork_repo.create(model.to_dict())
        except Exception as exc:
            raise ValidationError(f"Failed to create artwork: {exc}")
        return ArtworkResponse(success=True, message="Artwork created", artwork_id=str(inserted_id))


    def list_artworks(self, artist_id: str, limit=50, skip=0) -> list:
        docs = self.artwork_repo.find_by_artist(artist_id, limit=limit, skip=skip)
        for d in docs:
            key = d.get("s3_key")
            if key:
                try:
                    d["image_url"] = self.s3_service.generate_get_url(key, expires_in=3600)
                except Exception as e:
                    raise StorageServiceError(f"Could not generate signed image URL: {e}")
            d["artwork_id"] = str(d.pop("_id"))
        return docs


    def get_artwork(self, artist_id : str, artwork_id: str) -> dict:
        doc = self.artwork_repo.find_by_user_id_and_artwork_id(artist_id, artwork_id)
        if not doc:
            raise ArtworkNotFoundError("Artwork not found.")
        key = doc.get("s3_key")
        if key:
            doc["image_url"] = self.s3_service.generate_get_url(key, expires_in=3600)
        doc["artwork_id"] = str(doc.pop("_id"))
        return doc


    def update_artwork(self,artist_id : str, artwork_id: str, updates: dict) -> ArtworkResponse:
        if not updates:
            raise ValidationError("No updates provided.")

        ok = self.artwork_repo.update(artist_id, artwork_id, updates)
        if not ok:
            raise ArtworkNotFoundError("Artwork not found or update failed.")
        return ArtworkResponse(success=True, message="Artwork updated", artwork_id=artwork_id)

    def delete_artwork(self, artwork_id: str) -> ArtworkResponse:
        ok = self.artwork_repo.delete(artwork_id)
        if not ok:
            raise ArtworkNotFoundError("Artwork not found")
        return ArtworkResponse(success=True, message="Artwork deleted", artwork_id=artwork_id)


    def artist_summary(self, artist_id: str) -> dict:
        artworks = self.artwork_repo.find_by_artist(artist_id, limit=1000)
        total_artworks = len(artworks)

        order_repo = OrderRepository()
        orders = order_repo.find_by_artist(artist_id)
        total_sales = len(orders)
        pending_orders = sum(1 for o in orders if o.get("status") == "processing")
        earnings = sum(o.get("price", 0) for o in orders if o.get("status") == "completed")

        return {
            "total_artworks": total_artworks,
            "total_sales": total_sales,
            "pending_orders": pending_orders,
            "earnings": round(earnings, 2),
        }






