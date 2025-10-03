# app/services/artist_service.py
from app.dtos.requests.artwork_upload_request import ArtworkUploadRequest
from app.dtos.responses.artwork_response import ArtworkResponse
from app.persistence.artist_repository import ArtistRepository

class ArtistService:
    def __init__(self, artist_repository: ArtistRepository):
        self.artist_repository = artist_repository

    # Upload artwork
    def upload_artwork(self, artist_id: str, request_dto: ArtworkUploadRequest) -> ArtworkResponse:
        request_dto.validate()
        artwork_id = self.artist_repository.add_artwork(artist_id, vars(request_dto))
        return ArtworkResponse(success=True, message="Artwork uploaded", artwork_id=artwork_id)

    # Get all artworks
    def get_dashboard(self, artist_id: str):
        artworks = self.artist_repository.get_artworks(artist_id)
        return {"success": True, "artworks": artworks}

    # Update artwork
    def update_artwork(self, artwork_id: str, update_data: dict) -> ArtworkResponse:
        success = self.artist_repository.update_artwork(artwork_id, update_data)
        return ArtworkResponse(success=success, message="Artwork updated" if success else "Update failed")

    # Delete artwork
    def delete_artwork(self, artwork_id: str) -> ArtworkResponse:
        success = self.artist_repository.delete_artwork(artwork_id)
        return ArtworkResponse(success=success, message="Artwork deleted" if success else "Delete failed")
