# app/persistence/artist_repository.py
from flask import current_app
from app.extensions import mongo
from bson.objectid import ObjectId

class ArtistRepository:

    @staticmethod
    def _get_db():
        db_name = current_app.config["DB_NAME"]
        return mongo.cx[db_name]

    @staticmethod
    def add_artwork(artist_id: str, artwork_data: dict) -> str:
        db = ArtistRepository._get_db()
        artwork_data["artist_id"] = artist_id
        result = db["artworks"].insert_one(artwork_data)
        return str(result.inserted_id)

    @staticmethod
    def get_artworks(artist_id: str):
        db = ArtistRepository._get_db()
        return list(db["artworks"].find({"artist_id": artist_id}, {"_id": 0}))

    @staticmethod
    def update_artwork(artwork_id: str, update_data: dict) -> bool:
        db = ArtistRepository._get_db()
        try:
            obj_id = ObjectId(artwork_id)
        except Exception:
            return False
        result = db["artworks"].update_one({"_id": obj_id}, {"$set": update_data})
        return result.modified_count > 0

    @staticmethod
    def delete_artwork(artwork_id: str) -> bool:
        db = ArtistRepository._get_db()
        try:
            obj_id = ObjectId(artwork_id)
        except Exception:
            return False
        result = db["artworks"].delete_one({"_id": obj_id})
        return result.deleted_count > 0
