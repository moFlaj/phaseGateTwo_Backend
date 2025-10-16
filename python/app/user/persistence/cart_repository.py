# app/buyer/persistence/cart_repository.py
from flask import current_app
from bson import ObjectId
from app.extensions import mongo
from datetime import datetime

class CartRepository:
    COLLECTION = "carts"

    @staticmethod
    def _get_collection():
        db_name = current_app.config["DB_NAME"]
        return mongo.cx[db_name][CartRepository.COLLECTION]

    @staticmethod
    def create(cart_doc: dict) -> str:
        res = CartRepository._get_collection().insert_one(cart_doc)
        return str(res.inserted_id)

    @staticmethod
    def find_by_id(cart_id: str):
        try:
            _id = ObjectId(cart_id)
        except Exception:
            return None
        return CartRepository._get_collection().find_one({"_id": _id})

    @staticmethod
    def find_by_buyer(buyer_id: str):
        """Find active cart for buyer."""
        return CartRepository._get_collection().find_one({"buyer_id": buyer_id})

    @staticmethod
    def find_by_id_and_buyer(cart_id: str, buyer_id: str):
        """Find cart by ID and verify it belongs to the buyer."""
        try:
            _id = ObjectId(cart_id)
        except Exception:
            return None
        return CartRepository._get_collection().find_one({"_id": _id, "buyer_id": buyer_id})

    @staticmethod
    def update_items(cart_id: str, items: list):
        try:
            _id = ObjectId(cart_id)
        except Exception:
            return False
        result = CartRepository._get_collection().update_one(
            {"_id": _id}, {"$set": {"items": items}}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(cart_id: str):
        try:
            _id = ObjectId(cart_id)
        except Exception:
            return False
        CartRepository._get_collection().delete_one({"_id": _id})
        return True