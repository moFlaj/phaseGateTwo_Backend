import uuid
from typing import Dict, Any
from app.shared.exceptions.custom_errors import ValidationError


class MockPaystackService:
    """Mock Paystack service for testing without real payments."""
    
    def __init__(self):
        self.transactions = {}
        self.recipients = {}

    def initialize_transaction(self, email: str, amount: int, reference: str = None, 
                             callback_url: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Initialize a mock Paystack transaction."""
        if not reference:
            reference = f"txn_{uuid.uuid4().hex[:8]}"
            
        # Store transaction data
        self.transactions[reference] = {
            "reference": reference,
            "email": email,
            "amount": amount,
            "status": "initialized",
            "metadata": metadata or {}
        }
        
        return {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": f"http://localhost:5000/mock-paystack/authorize/{reference}",
                "access_code": f"ac_{uuid.uuid4().hex[:8]}",
                "reference": reference
            }
        }

    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify a mock Paystack transaction."""
        if reference not in self.transactions:
            raise ValidationError("Transaction not found")
            
        transaction = self.transactions[reference]
        transaction["status"] = "success"
        
        return {
            "status": True,
            "message": "Verification successful",
            "data": {
                "status": "success",
                "reference": reference,
                "amount": transaction["amount"],
                "customer": {
                    "email": transaction["email"]
                },
                "metadata": transaction["metadata"]
            }
        }

    def create_transfer_recipient(self, name: str, account_number: str, bank_code: str,
                                currency: str = "NGN") -> Dict[str, Any]:
        """Create a mock transfer recipient."""
        recipient_code = f"RCP_{uuid.uuid4().hex[:8]}"
        
        self.recipients[recipient_code] = {
            "recipient_code": recipient_code,
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": currency
        }
        
        return {
            "status": True,
            "message": "Recipient created",
            "data": {
                "recipient_code": recipient_code,
                "name": name,
                "account_number": account_number,
                "bank_code": bank_code
            }
        }

    def initiate_transfer(self, amount: int, recipient_code: str, reason: str = None,
                         reference: str = None) -> Dict[str, Any]:
        """Initiate a mock transfer."""
        if recipient_code not in self.recipients:
            raise ValidationError("Recipient not found")
            
        if not reference:
            reference = f"trf_{uuid.uuid4().hex[:8]}"
            
        return {
            "status": True,
            "message": "Transfer initiated",
            "data": {
                "reference": reference,
                "amount": amount,
                "recipient": recipient_code,
                "status": "success"
            }
        }