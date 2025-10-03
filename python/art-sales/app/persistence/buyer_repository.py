# app/persistence/buyer_repository.py
from flask import current_app
from app.extensions import mongo
from bson.objectid import ObjectId

class BuyerRepository:

    @staticmethod
    def _get_db():
        db_name = current_app.config["DB_NAME"]
        return mongo.cx[db_name]

    @staticmethod
    def update_profile(buyer_id: str, update_data: dict) -> bool:
        try:
            obj_id = ObjectId(buyer_id)
        except Exception:
            return False
        result = BuyerRepository._get_db()["users"].update_one({"_id": obj_id}, {"$set": update_data})
        return result.modified_count > 0

    @staticmethod
    def add_to_cart(buyer_id: str, artwork_id: str, quantity: int = 1):
        db = BuyerRepository._get_db()
        cart_collection = db["carts"]
        # upsert cart item
        cart_collection.update_one(
            {"buyer_id": buyer_id, "artwork_id": artwork_id},
            {"$set": {"quantity": quantity}},
            upsert=True
        )

    @staticmethod
    def get_cart(buyer_id: str):
        db = BuyerRepository._get_db()
        items = list(db["carts"].find({"buyer_id": buyer_id}, {"_id": 0}))
        return items

    @staticmethod
    def add_order(buyer_id: str, order_data: dict):
        db = BuyerRepository._get_db()
        db["orders"].insert_one({"buyer_id": buyer_id, **order_data})

    @staticmethod
    def get_orders(buyer_id: str):
        db = BuyerRepository._get_db()
        return list(db["orders"].find({"buyer_id": buyer_id}, {"_id": 0}))
