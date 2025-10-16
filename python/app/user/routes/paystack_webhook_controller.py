# app/buyer/routes/paystack_webhook_controller.py
from flask import Blueprint, request, jsonify, current_app
from app.user.services.paystack_checkout_service import PaystackCheckoutService
from app.user.persistence.cart_repository import CartRepository
from app.user.persistence.order_repository import OrderRepository
from app.shared.exceptions.custom_errors import ValidationError
from typing import Any

paystack_webhook_bp = Blueprint("paystack_webhook_bp", __name__, url_prefix="/paystack")

# Global service instance
webhook_service: Any = None
email_service: Any = None

def init_services(email_service_instance=None) -> None:
    """Initialize the webhook service."""
    global webhook_service, email_service
    email_service = email_service_instance
    webhook_service = PaystackCheckoutService(CartRepository(), OrderRepository())


@paystack_webhook_bp.route("/webhook", methods=["POST"])
def paystack_webhook():
    """
    Handle Paystack webhook events.
    """
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({"success": False, "message": "Invalid payload"}), 400
            
        # Extract event data
        event = payload.get("event")
        data = payload.get("data", {})
        
        if event == "charge.success":
            # Payment was successful
            reference = data.get("reference")
            if reference:
                try:
                    result = webhook_service.verify_payment(reference, email_service)
                    return jsonify(result), 200
                except Exception as e:
                    return jsonify({"success": False, "message": str(e)}), 400
        
        # For other events, just acknowledge receipt
        return jsonify({"success": True, "message": "Webhook received"}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500