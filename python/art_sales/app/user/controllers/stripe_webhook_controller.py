# app/buyer/routes/stripe_webhook_controller.py
from typing import Any
from flask import Blueprint, request, jsonify, current_app
from app.buyer.services.stripe_webhook_service import StripeWebhookService
from app.buyer.persistence.cart_repository import CartRepository
from app.buyer.persistence.order_repository import OrderRepository
from app.artist.persistence.artwork_repository import ArtworkRepository
from app.shared.exceptions.custom_errors import PaymentVerificationError, CartNotFoundError, DuplicateOrderError

stripe_webhook_bp = Blueprint("stripe_webhook_bp", __name__, url_prefix="/stripe")

# These will be injected during app startup
email_service: Any = None
webhook_service: StripeWebhookService | None = None

def init_services(email_service_instance) -> None:
    """
    Wire the correct EmailService instance into the webhook controller.
    This mirrors how auth_controller does it.
    """
    global email_service, webhook_service
    email_service = email_service_instance
    current_app.config["EMAIL_SERVICE"] = email_service

    # Initialize a reusable service instance for webhook handling
    webhook_service = StripeWebhookService(
        CartRepository(),
        OrderRepository(),
        ArtworkRepository(),
        email_service
    )


@stripe_webhook_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")

    try:
        import json
        parsed = json.loads(payload)
    except Exception:
        parsed = {}

    try:
        result = webhook_service.handle_event(parsed, sig_header)
        return jsonify(result), 200
    except (PaymentVerificationError, CartNotFoundError) as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except DuplicateOrderError as e:
        return jsonify({"success": False, "message": str(e)}), 409
    except Exception as e:
        print("Unhandled webhook error:", e)
        return jsonify({"success": False, "message": "Webhook processing failed."}), 500
