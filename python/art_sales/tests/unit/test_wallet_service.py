import pytest
from unittest.mock import Mock, patch
from app.wallet.services.wallet_service import WalletService
from app.wallet.persistence.repository import WalletRepository
from app.wallet.domain.models import Wallet, WalletTransaction, TransactionType, TransactionStatus
from app.shared.exceptions.custom_errors import ValidationError
from bson import ObjectId


class TestWalletService:
    """Test cases for WalletService."""
    
    def test_create_wallet_new(self):
        """Test creating a new wallet."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        mock_repository.find_by_user_id.return_value = None
        mock_repository.create.return_value = ObjectId("507f1f77bcf86cd799439011")
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test the method
        user_id = "user123"
        wallet = service.create_wallet(user_id)
        
        # Assertions
        assert wallet.user_id == user_id
        assert wallet.balance == 0.0
        mock_repository.create.assert_called_once()
    
    def test_create_wallet_existing(self):
        """Test creating a wallet that already exists."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        existing_wallet = Wallet(user_id="user123", balance=100.0)
        mock_repository.find_by_user_id.return_value = existing_wallet
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test the method
        user_id = "user123"
        wallet = service.create_wallet(user_id)
        
        # Assertions
        assert wallet.user_id == user_id
        assert wallet.balance == 100.0
        mock_repository.create.assert_not_called()
    
    def test_deposit(self):
        """Test depositing funds."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        wallet = Wallet(user_id="user123", balance=50.0)
        mock_repository.find_by_user_id.return_value = wallet
        mock_repository.update.return_value = True
        mock_repository.create_transaction.return_value = "txn123"
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test the method
        updated_wallet = service.deposit("user123", 25.0, "test_ref")
        
        # Assertions
        assert updated_wallet.balance == 75.0
        mock_repository.update.assert_called_once()
        mock_repository.create_transaction.assert_called_once()
    
    def test_deposit_invalid_amount(self):
        """Test depositing invalid amount."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test with invalid amount
        with pytest.raises(ValidationError):
            service.deposit("user123", -25.0, "test_ref")
    
    def test_withdraw_success(self):
        """Test successful withdrawal."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        wallet = Wallet(user_id="user123", balance=50.0)
        mock_repository.find_by_user_id.return_value = wallet
        mock_repository.update.return_value = True
        mock_repository.create_transaction.return_value = "txn123"
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test the method
        success = service.withdraw("user123", 25.0, "test_ref")
        
        # Assertions
        assert success is True
        assert wallet.balance == 25.0
        mock_repository.update.assert_called_once()
        mock_repository.create_transaction.assert_called_once()
    
    def test_withdraw_insufficient_funds(self):
        """Test withdrawal with insufficient funds."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        wallet = Wallet(user_id="user123", balance=25.0)
        mock_repository.find_by_user_id.return_value = wallet
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test the method
        success = service.withdraw("user123", 50.0, "test_ref")
        
        # Assertions
        assert success is False
        assert wallet.balance == 25.0
        mock_repository.update.assert_not_called()
    
    def test_withdraw_invalid_amount(self):
        """Test withdrawal with invalid amount."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test with invalid amount
        with pytest.raises(ValidationError):
            service.withdraw("user123", -50.0, "test_ref")
    
    def test_transfer_success(self):
        """Test successful transfer between wallets."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        from_wallet = Wallet(user_id="user1", balance=100.0)
        to_wallet = Wallet(user_id="user2", balance=50.0)
        
        mock_repository.find_by_user_id.side_effect = [from_wallet, to_wallet]
        mock_repository.update.return_value = True
        mock_repository.create_transaction.return_value = "txn123"
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test the method
        success = service.transfer("user1", "user2", 25.0)
        
        # Assertions
        assert success is True
        assert from_wallet.balance == 75.0
        assert to_wallet.balance == 75.0
        assert mock_repository.update.call_count == 2
        assert mock_repository.create_transaction.call_count == 2
    
    def test_transfer_insufficient_funds(self):
        """Test transfer with insufficient funds."""
        # Mock the repository
        mock_repository = Mock(spec=WalletRepository)
        from_wallet = Wallet(user_id="user1", balance=20.0)
        to_wallet = Wallet(user_id="user2", balance=50.0)
        
        mock_repository.find_by_user_id.side_effect = [from_wallet, to_wallet]
        
        # Create service with mock repository
        service = WalletService(mock_repository)
        
        # Test the method
        success = service.transfer("user1", "user2", 25.0)
        
        # Assertions
        assert success is False
        assert from_wallet.balance == 20.0  # No change
        assert to_wallet.balance == 50.0    # No change
        mock_repository.update.assert_not_called()