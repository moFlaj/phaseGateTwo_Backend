# app/buyer/persistence/order_repository.py
from typing import Optional, List
from bson import ObjectId
from flask import current_app
from app.extensions import mongo


class OrderRepository:
    COLLECTION = "orders"

    @staticmethod
    def _col():
        db_name = current_app.config["DB_NAME"]
        return mongo.cx[db_name][OrderRepository.COLLECTION]

    @staticmethod
    def create(payload: dict) -> ObjectId:
        payload["created_at"] = __import__("datetime").datetime.utcnow()
        result = OrderRepository._col().insert_one(payload)
        return result.inserted_id

    @staticmethod
    def find_by_buyer(buyer_id: str, limit: int = 50, skip: int = 0) -> List[dict]:
        cursor = OrderRepository._col().find({"buyer_id": buyer_id}).skip(skip).limit(limit)
        return list(cursor)

    @staticmethod
    def find_by_artist(artist_id: str, limit: int = 50, skip: int = 0) -> List[dict]:
        cursor = OrderRepository._col().find({"artist_id": artist_id}).skip(skip).limit(limit)
        return list(cursor)

    @staticmethod
    def find_by_id(order_id: str) -> Optional[dict]:
        try:
            _id = ObjectId(order_id)
        except Exception:
            return None
        return OrderRepository._col().find_one({"_id": _id})

    @staticmethod
    def find_by_reference(reference: str) -> List[dict]:
        """Find orders by Paystack reference."""
        return list(OrderRepository._col().find({"reference": reference}))

    @staticmethod
    def find_duplicate(buyer_id: str, artwork_id: str):
        """Prevent duplicate active orders for the same artwork."""
        return OrderRepository._col().find_one({
            "buyer_id": buyer_id,
            "artwork_id": artwork_id,
            "status": {"$ne": "cancelled"}
        })

    @staticmethod
    def update_status(order_id: str, new_status: str) -> bool:
        try:
            _id = ObjectId(order_id)
        except Exception:
            return False
        result = OrderRepository._col().update_one(
            {"_id": _id}, {"$set": {"status": new_status}}
        )
        return result.modified_count > 0

    @staticmethod
    def mark_paid_by_reference(reference: str) -> int:
        """Mark all orders with this reference as 'completed' after successful payment."""
        result = OrderRepository._col().update_many(
            {"reference": reference},
            {"$set": {"status": "completed"}}
        )
        return result.modified_count

    @staticmethod
    def count_completed_orders_by_artist(artist_id: str) -> int:
        """Count the number of completed orders for an artist."""
        return OrderRepository._col().count_documents({
            "artist_id": artist_id,
            "status": "completed"
        })

    @staticmethod
    def calculate_earnings_by_artist(artist_id: str) -> float:
        """Calculate total earnings for an artist from completed orders."""
        pipeline = [
            {
                "$match": {
                    "artist_id": artist_id,
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_earnings": {"$sum": {"$multiply": ["$price", "$quantity"]}}
                }
            }
        ]
        result = list(OrderRepository._col().aggregate(pipeline))
        return result[0]["total_earnings"] if result else 0.0
