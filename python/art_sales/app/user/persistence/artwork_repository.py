# app/artist/persistence/artwork_repository.py
from typing import Optional, List
from bson import ObjectId
from flask import current_app
from app.extensions import mongo
from pymongo import TEXT

from app.shared.exceptions.custom_errors import ValidationError, InvalidPriceRangeError


class ArtworkRepository:
    COLLECTION = "artworks"

    @staticmethod
    def _get_collection():
        db_name = current_app.config["DB_NAME"]
        return mongo.cx[db_name][ArtworkRepository.COLLECTION]

    @staticmethod
    def create(payload: dict) -> ObjectId:
        payload["created_at"] = __import__("datetime").datetime.utcnow()
        result = ArtworkRepository._get_collection().insert_one(payload)
        return result.inserted_id

    @staticmethod
    def find_by_artist(artist_id: str, limit: int = 50, skip: int = 0) -> List[dict]:
        cursor = ArtworkRepository._get_collection().find({"artist_id": artist_id}).skip(skip).limit(limit)
        return list(cursor)

    @staticmethod
    def find_by_id(artwork_id: str) -> Optional[dict]:
        try:
            _id = ObjectId(artwork_id)
        except Exception:
            return None
        return ArtworkRepository._get_collection().find_one({"_id": _id})

    @staticmethod
    def find_by_user_id_and_artwork_id(artist_id : str, artwork_id: str) -> Optional[dict]:
        try:
            _id = ObjectId(artwork_id)
        except Exception:
            return None
        return ArtworkRepository._get_collection().find_one({"artist_id": artist_id, "_id": _id})

    @staticmethod
    def update(artist_id : str, artwork_id: str, updates: dict) -> bool:
        try:
            _id = ObjectId(artwork_id)
        except Exception:
            return False
        res = ArtworkRepository._get_collection().update_one({"_id": _id, "artist_id": artist_id}, {"$set": updates})
        return res.modified_count > 0

    @staticmethod
    def delete(artwork_id: str) -> bool:
        try:
            _id = ObjectId(artwork_id)
        except Exception:
            return False
        res = ArtworkRepository._get_collection().delete_one({"_id": _id})
        return res.deleted_count > 0

    def search_artworks(self, query: Optional[str] = None,
                        min_price: float = 0.0,
                        max_price: float = 1_000_000.0,
                        limit: int = 50,
                        skip: int = 0) -> List[dict]:
        """
        Simple text + price range search.
        - Uses a text index on (title, description).
        - Returns list of artwork dicts with artwork_id set.
        """
        # Validate price range
        try:
            min_price = float(min_price)
            max_price = float(max_price)
        except Exception:
            raise InvalidPriceRangeError("Price range values must be numbers.")

        if min_price < 0 or max_price <= 0 or min_price > max_price:
            raise InvalidPriceRangeError("Invalid price range.")

        coll = ArtworkRepository._get_collection()

        # Ensure a text index exists (no-op if already present)
        try:
            coll.create_index([("title", TEXT), ("description", TEXT)], name="text_index", default_language="english")
        except Exception:
            # ignore index creation errors (race or already exists)
            pass

        filters = {"price": {"$gte": min_price, "$lte": max_price}}
        if query:
            filters["$text"] = {"$search": query}

        cursor = coll.find(filters).skip(int(skip)).limit(int(limit))
        results = list(cursor)
        for r in results:
            r["artwork_id"] = str(r.pop("_id"))
        return results

    @staticmethod
    def count_by_artist(artist_id: str) -> int:
        """Count the number of artworks for an artist."""
        return ArtworkRepository._get_collection().count_documents({"artist_id": artist_id})
