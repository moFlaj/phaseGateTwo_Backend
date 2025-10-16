# app/persistence/verification_repository.py
from pymongo import ASCENDING
from flask import current_app
from app.extensions import mongo
from app.auth.domain.verification_model import Verification


class VerificationRepository:
    COLLECTION_NAME = "email_verifications"

    @staticmethod
    def _get_collection():
        db_name = current_app.config["DB_NAME"]
        coll = mongo.cx[db_name][VerificationRepository.COLLECTION_NAME]
        # TTL index: 5 minutes
        coll.create_index([("created_at", ASCENDING)], expireAfterSeconds=300)
        coll.create_index("email", unique=True)
        return coll

    @staticmethod
    def find_by_email(email: str):
        """Fetch verification record by email."""
        return VerificationRepository._get_collection().find_one({"email": email})

    @staticmethod
    def save(verification: Verification):
        """Insert or update verification record."""
        VerificationRepository._get_collection().replace_one(
            {"email": verification.email}, verification.to_dict(), upsert=True
        )

    @staticmethod
    def delete_by_email(email: str):
        """Delete verification record for a given email."""
        VerificationRepository._get_collection().delete_many({"email": email})
