import requests
import os
from typing import Dict, Any, Optional
from app.shared.exceptions.custom_errors import ValidationError


class PaystackService:
    """Service for Paystack payment integration."""
    
    def __init__(self):
        self.secret_key = os.getenv("PAYSTACK_SECRET_KEY", "")
        self.base_url = "https://api.paystack.co"
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def initialize_transaction(self, email: str, amount: int, reference: str = None, 
                             callback_url: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Initialize a Paystack transaction."""
        if not self.secret_key:
            raise ValidationError("Paystack secret key not configured")
            
        payload = {
            "email": email,
            "amount": amount,  # Amount in kobo (smallest currency unit)
            "reference": reference,
            "callback_url": callback_url,
            "metadata": metadata or {}
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to initialize Paystack transaction: {str(e)}")

    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify a Paystack transaction."""
        if not self.secret_key:
            raise ValidationError("Paystack secret key not configured")
            
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to verify Paystack transaction: {str(e)}")

    def create_transfer_recipient(self, name: str, account_number: str, bank_code: str,
                                currency: str = "NGN") -> Dict[str, Any]:
        """Create a transfer recipient."""
        if not self.secret_key:
            raise ValidationError("Paystack secret key not configured")
            
        payload = {
            "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": currency
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transferrecipient",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to create transfer recipient: {str(e)}")

    def initiate_transfer(self, amount: int, recipient_code: str, reason: str = None,
                         reference: str = None) -> Dict[str, Any]:
        """Initiate a transfer."""
        if not self.secret_key:
            raise ValidationError("Paystack secret key not configured")
            
        payload = {
            "source": "balance",
            "amount": amount,
            "recipient": recipient_code,
            "reason": reason,
            "reference": reference
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        try:
            response = requests.post(
                f"{self.base_url}/transfer",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Failed to initiate transfer: {str(e)}")