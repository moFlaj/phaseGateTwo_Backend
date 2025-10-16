# app/buyer/routes/checkout_controller.py
from flask import Blueprint, request, jsonify, g
from app.shared.utilities.jwt_utils import token_required, role_required
from app.user.persistence.cart_repository import CartRepository
from app.user.services.paystack_checkout_service import PaystackCheckoutService
from app.shared.exceptions.custom_errors import ValidationError

checkout_bp = Blueprint("checkout_bp", __name__, url_prefix="/checkout")

def _get_buyer_id():
    user = getattr(g, "user", None)
    if not user:
        raise ValidationError("Missing authenticated user.")
    return user.get("user_id")

@checkout_bp.route("/create-session", methods=["POST"])
@token_required
@role_required("buyer")
def create_session():
    data = request.get_json(force=True) or {}
    cart_id = data.get("cart_id")
    if not cart_id:
        return jsonify({"success": False, "message": "Missing cart_id"}), 400
    buyer_id = _get_buyer_id()
    svc = PaystackCheckoutService(CartRepository())
    try:
        session = svc.create_checkout_session(buyer_id, cart_id)
        return jsonify({"success": True, **session}), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500