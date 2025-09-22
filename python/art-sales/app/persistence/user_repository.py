from flask import current_app
from bson.objectid import ObjectId

from app.extensions import mongo
from app.models.user_model import User


class UserRepository:

    @staticmethod
    def _get_user_collection():
        db_name = current_app.config["DB_NAME"]
        return mongo.cx[db_name]["users"]

    @staticmethod
    def find_by_email(email: str) -> dict | None:
        """
        Find a user document by email.
        Returns the Mongo document as dict if found, else None.
        """
        return UserRepository._get_user_collection().find_one({"email": email})

    @staticmethod
    def find_by_id(user_id: str) -> dict | None:
        """
        Find a user document by _id.
        """
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            return None
        return UserRepository._get_user_collection().find_one({"_id": obj_id})

    @staticmethod
    def insert_user(user: User) -> str:
        """
        Insert a user document into the 'users' collection.
        Accepts a User dataclass instance.
        Returns inserted document id as string.
        """
        result = UserRepository._get_user_collection().insert_one(user.to_dict())
        return str(result.inserted_id)

    @staticmethod
    def update_user(user_id: str, update_data: dict) -> bool:
        """
        Update user document fields given user_id.
        Returns True if update was acknowledged and modified count > 0.
        """
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            return False
        result = UserRepository._get_user_collection().update_one({"_id": obj_id}, {"$set": update_data})
        return result.modified_count > 0

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        Delete a user by _id.
        Returns True if delete was successful.
        """
        try:
            obj_id = ObjectId(user_id)
        except Exception:
            return False
        result = UserRepository._get_user_collection().delete_one({"_id": obj_id})
        return result.deleted_count > 0
