from typing import Optional
from datetime import datetime, UTC
from bson import ObjectId
from app.wallet.domain.models import Wallet, WalletTransaction, TransactionType, TransactionStatus
from app.wallet.persistence.repository import WalletRepository
from app.shared.exceptions.custom_errors import ValidationError


class WalletService:
    """Service for wallet business logic."""
    
    def __init__(self, wallet_repository: WalletRepository):
        self.wallet_repository = wallet_repository

    def create_wallet(self, user_id: str) -> Wallet:
        """Create a new wallet for a user."""
        # Check if wallet already exists
        existing_wallet = self.wallet_repository.find_by_user_id(user_id)
        if existing_wallet:
            return existing_wallet
            
        wallet = Wallet(user_id=user_id)
        wallet_id = self.wallet_repository.create(wallet)
        wallet._id = ObjectId(wallet_id)
        return wallet

    def get_wallet(self, user_id: str) -> Optional[Wallet]:
        """Get wallet for a user."""
        return self.wallet_repository.find_by_user_id(user_id)

    def deposit(self, user_id: str, amount: float, reference: str = "") -> Wallet:
        """Deposit funds into user's wallet."""
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
            
        wallet = self.get_wallet(user_id)
        if not wallet:
            wallet = self.create_wallet(user_id)
            
        wallet.balance += amount
        wallet.updated_at = datetime.now(UTC)
        self.wallet_repository.update(wallet)
        
        # Record transaction
        transaction = WalletTransaction(
            wallet_id=str(wallet._id),
            amount=amount,
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            description=f"Deposit of {amount} NGN",
            reference=reference
        )
        self.wallet_repository.create_transaction(transaction)
        
        return wallet

    def withdraw(self, user_id: str, amount: float, reference: str = "") -> bool:
        """Withdraw funds from user's wallet."""
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")
            
        wallet = self.get_wallet(user_id)
        if not wallet:
            raise ValidationError("Wallet not found")
            
        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.updated_at = datetime.now(UTC)
            self.wallet_repository.update(wallet)
            
            # Record transaction
            transaction = WalletTransaction(
                wallet_id=str(wallet._id),
                amount=amount,
                transaction_type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.COMPLETED,
                description=f"Withdrawal of {amount} NGN",
                reference=reference
            )
            self.wallet_repository.create_transaction(transaction)
            return True
        return False

    def transfer(self, from_user_id: str, to_user_id: str, amount: float) -> bool:
        """Transfer funds between users."""
        if amount <= 0:
            raise ValidationError("Transfer amount must be positive")
            
        from_wallet = self.get_wallet(from_user_id)
        to_wallet = self.get_wallet(to_user_id)
        
        if not from_wallet:
            raise ValidationError("Sender wallet not found")
        if not to_wallet:
            to_wallet = self.create_wallet(to_user_id)
            
        # Attempt withdrawal
        if from_wallet.balance < amount:
            return False
            
        # Process transfer
        from_wallet.balance -= amount
        to_wallet.balance += amount
        from_wallet.updated_at = datetime.now(UTC)
        to_wallet.updated_at = datetime.now(UTC)
        
        # Update both wallets
        self.wallet_repository.update(from_wallet)
        self.wallet_repository.update(to_wallet)
        
        # Record transactions for both wallets
        from_transaction = WalletTransaction(
            wallet_id=str(from_wallet._id),
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
            status=TransactionStatus.COMPLETED,
            description=f"Transfer of {amount} NGN to user {to_user_id}",
            related_wallet_id=str(to_wallet._id)
        )
        self.wallet_repository.create_transaction(from_transaction)
        
        to_transaction = WalletTransaction(
            wallet_id=str(to_wallet._id),
            amount=amount,
            transaction_type=TransactionType.TRANSFER,
            status=TransactionStatus.COMPLETED,
            description=f"Transfer of {amount} NGN from user {from_user_id}",
            related_wallet_id=str(from_wallet._id)
        )
        self.wallet_repository.create_transaction(to_transaction)
        
        return True

    def get_transaction(self, transaction_id: str) -> Optional[WalletTransaction]:
        """Get a specific transaction."""
        return self.wallet_repository.find_transaction_by_id(transaction_id)