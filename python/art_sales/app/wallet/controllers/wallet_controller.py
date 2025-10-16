from flask import Blueprint, request, jsonify, current_app
from app.wallet.services.wallet_service import WalletService
from app.wallet.persistence.repository import WalletRepository
from app.wallet.services.paystack_service import PaystackService
from app.wallet.services.mock_paystack_service import MockPaystackService
from app.shared.exceptions.custom_errors import ValidationError
from typing import Any
import os

# Global service instances
wallet_service: Any = None
paystack_service: Any = None
use_mock_paystack: bool = False

wallet_bp = Blueprint("wallet", __name__, url_prefix="/wallet")


def init_wallet_service() -> None:
    """Initialize the wallet service."""
    global wallet_service, paystack_service, use_mock_paystack
    wallet_repository = WalletRepository()
    wallet_service = WalletService(wallet_repository)
    
    # Check if we should use mock Paystack
    use_mock_paystack = os.getenv("USE_MOCK_PAYSTACK", "True") == "True"
    if use_mock_paystack:
        paystack_service = MockPaystackService()
    else:
        paystack_service = PaystackService()


@wallet_bp.route("/balance", methods=["GET"])
def get_balance():
    """Get user's wallet balance."""
    try:
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return jsonify({"success": False, "message": "User ID required"}), 400
            
        wallet = wallet_service.get_wallet(user_id)
        if not wallet:
            return jsonify({"success": False, "message": "Wallet not found"}), 404
            
        return jsonify({
            "success": True,
            "balance": wallet.balance,
            "currency": wallet.currency
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@wallet_bp.route("/deposit", methods=["POST"])
def deposit():
    """Deposit funds into wallet."""
    try:
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return jsonify({"success": False, "message": "User ID required"}), 400
            
        data = request.get_json()
        amount = data.get("amount")
        reference = data.get("reference", "")
        
        if not amount or amount <= 0:
            return jsonify({"success": False, "message": "Valid amount required"}), 400
            
        wallet = wallet_service.deposit(user_id, amount, reference)
        
        return jsonify({
            "success": True,
            "message": "Deposit successful",
            "balance": wallet.balance
        }), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@wallet_bp.route("/withdraw", methods=["POST"])
def withdraw():
    """Withdraw funds from wallet."""
    try:
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return jsonify({"success": False, "message": "User ID required"}), 400
            
        data = request.get_json()
        amount = data.get("amount")
        reference = data.get("reference", "")
        
        if not amount or amount <= 0:
            return jsonify({"success": False, "message": "Valid amount required"}), 400
            
        success = wallet_service.withdraw(user_id, amount, reference)
        if success:
            return jsonify({
                "success": True,
                "message": "Withdrawal successful"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Insufficient funds"
            }), 400
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@wallet_bp.route("/paystack/initialize", methods=["POST"])
def initialize_paystack_payment():
    """Initialize a Paystack payment."""
    try:
        user_id = request.headers.get("X-User-ID")
        if not user_id:
            return jsonify({"success": False, "message": "User ID required"}), 400
            
        data = request.get_json()
        email = data.get("email")
        amount = data.get("amount")  # in NGN, will be converted to kobo
        
        if not email or not amount:
            return jsonify({"success": False, "message": "Email and amount required"}), 400
            
        # Convert NGN to kobo (smallest unit)
        amount_kobo = int(amount * 100)
        
        # Initialize Paystack transaction
        response = paystack_service.initialize_transaction(
            email=email,
            amount=amount_kobo,
            metadata={"user_id": user_id}
        )
        
        return jsonify({
            "success": True,
            "data": response.get("data", {})
        }), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@wallet_bp.route("/paystack/webhook", methods=["POST"])
def paystack_webhook():
    """Handle Paystack webhook for payment verification."""
    try:
        # In a real implementation, you would verify the webhook signature
        # For now, we'll just process the payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({"success": False, "message": "Invalid payload"}), 400
            
        # Extract relevant data
        event = payload.get("event")
        data = payload.get("data", {})
        
        if event == "charge.success":
            # Payment was successful
            reference = data.get("reference")
            amount = data.get("amount")  # in kobo
            metadata = data.get("metadata", {})
            user_id = metadata.get("user_id")
            
            if user_id and amount:
                # Convert kobo to NGN
                amount_ngn = amount / 100
                
                # Deposit funds into user's wallet
                wallet = wallet_service.deposit(user_id, amount_ngn, reference)
                
                return jsonify({
                    "success": True,
                    "message": "Payment processed and wallet updated"
                }), 200
        
        return jsonify({"success": True, "message": "Webhook received"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@wallet_bp.route("/paystack/verify/<reference>", methods=["POST"])
def verify_paystack_payment(reference):
    """Verify a Paystack payment (for testing)."""
    try:
        # Verify the transaction
        response = paystack_service.verify_transaction(reference)
        
        if response.get("status") and response.get("data", {}).get("status") == "success":
            # Payment was successful, update wallet
            data = response.get("data", {})
            amount = data.get("amount")  # in kobo
            metadata = data.get("metadata", {})
            user_id = metadata.get("user_id")
            
            if user_id and amount:
                # Convert kobo to NGN
                amount_ngn = amount / 100
                
                # Deposit funds into user's wallet
                wallet = wallet_service.deposit(user_id, amount_ngn, reference)
                
                return jsonify({
                    "success": True,
                    "message": "Payment verified and wallet updated",
                    "balance": wallet.balance
                }), 200
        
        return jsonify({
            "success": False,
            "message": "Payment verification failed"
        }), 400
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500