from typing import Optional
from bson import ObjectId
from app.extensions import mongo
from app.wallet.domain.models import Wallet, WalletTransaction
import os


class WalletRepository:
    """Repository for wallet persistence operations."""
    
    COLLECTION_NAME = "wallets"
    TRANSACTION_COLLECTION_NAME = "wallet_transactions"

    @staticmethod
    def _get_collection():
        """Get the wallets collection."""
        db_name = os.getenv("DB_NAME", "art_sales_db")
        return mongo.cx[db_name][WalletRepository.COLLECTION_NAME]

    @staticmethod
    def _get_transaction_collection():
        """Get the wallet transactions collection."""
        db_name = os.getenv("DB_NAME", "art_sales_db")
        return mongo.cx[db_name][WalletRepository.TRANSACTION_COLLECTION_NAME]

    def find_by_user_id(self, user_id: str) -> Optional[Wallet]:
        """Find wallet by user ID."""
        data = self._get_collection().find_one({"user_id": user_id})
        return Wallet.from_dict(data) if data else None

    def find_by_id(self, wallet_id: str) -> Optional[Wallet]:
        """Find wallet by ID."""
        data = self._get_collection().find_one({"_id": ObjectId(wallet_id)})
        return Wallet.from_dict(data) if data else None

    def create(self, wallet: Wallet) -> str:
        """Create a new wallet."""
        data = wallet.to_dict()
        result = self._get_collection().insert_one(data)
        return str(result.inserted_id)

    def update(self, wallet: Wallet) -> bool:
        """Update an existing wallet."""
        if not wallet._id:
            return False
        data = wallet.to_dict()
        result = self._get_collection().update_one(
            {"_id": wallet._id}, 
            {"$set": data}
        )
        return result.modified_count > 0

    def delete(self, wallet_id: str) -> bool:
        """Delete a wallet."""
        result = self._get_collection().delete_one({"_id": ObjectId(wallet_id)})
        return result.deleted_count > 0

    # Transaction methods
    def create_transaction(self, transaction: WalletTransaction) -> str:
        """Create a new wallet transaction."""
        data = transaction.to_dict()
        result = self._get_transaction_collection().insert_one(data)
        return str(result.inserted_id)

    def update_transaction(self, transaction: WalletTransaction) -> bool:
        """Update an existing wallet transaction."""
        if not transaction._id:
            return False
        data = transaction.to_dict()
        result = self._get_transaction_collection().update_one(
            {"_id": transaction._id}, 
            {"$set": data}
        )
        return result.modified_count > 0

    def find_transaction_by_id(self, transaction_id: str) -> Optional[WalletTransaction]:
        """Find transaction by ID."""
        data = self._get_transaction_collection().find_one({"_id": ObjectId(transaction_id)})
        return WalletTransaction.from_dict(data) if data else None