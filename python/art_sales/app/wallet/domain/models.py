from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional
from bson import ObjectId
from enum import Enum


class TransactionType(Enum):
    """Types of wallet transactions."""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"


class TransactionStatus(Enum):
    """Status of wallet transactions."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Wallet:
    """Represents a user's wallet for storing funds."""
    user_id: str
    balance: float = 0.0
    currency: str = "NGN"  # Nigerian Naira
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _id: Optional[ObjectId] = None

    def to_dict(self) -> dict:
        """Convert wallet to dictionary for database storage."""
        data = {
            "user_id": self.user_id,
            "balance": self.balance,
            "currency": self.currency,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self._id:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Wallet':
        """Create wallet from dictionary data."""
        wallet = cls(
            user_id=data["user_id"],
            balance=data.get("balance", 0.0),
            currency=data.get("currency", "NGN"),
            created_at=data.get("created_at", datetime.now(UTC)),
            updated_at=data.get("updated_at", datetime.now(UTC))
        )
        if "_id" in data:
            wallet._id = data["_id"]
        return wallet


@dataclass
class WalletTransaction:
    """Represents a transaction in a wallet."""
    wallet_id: str
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING
    description: str = ""
    reference: str = ""
    related_wallet_id: Optional[str] = None  # For transfers
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _id: Optional[ObjectId] = None

    def to_dict(self) -> dict:
        """Convert transaction to dictionary for database storage."""
        data = {
            "wallet_id": self.wallet_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "status": self.status.value,
            "description": self.description,
            "reference": self.reference,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if self.related_wallet_id:
            data["related_wallet_id"] = self.related_wallet_id
        if self._id:
            data["_id"] = self._id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'WalletTransaction':
        """Create transaction from dictionary data."""
        transaction = cls(
            wallet_id=data["wallet_id"],
            amount=data["amount"],
            transaction_type=TransactionType(data["transaction_type"]),
            status=TransactionStatus(data.get("status", "pending")),
            description=data.get("description", ""),
            reference=data.get("reference", ""),
            related_wallet_id=data.get("related_wallet_id"),
            created_at=data.get("created_at", datetime.now(UTC)),
            updated_at=data.get("updated_at", datetime.now(UTC))
        )
        if "_id" in data:
            transaction._id = data["_id"]
        return transaction