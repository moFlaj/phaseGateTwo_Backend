# app/buyer/routes/cart_controller.py
from flask import Blueprint, request, jsonify, g
from app.utilities.jwt_utils import token_required, role_required
from app.buyer.persistence.cart_repository import CartRepository
from app.artist.persistence.artwork_repository import ArtworkRepository
from app.buyer.services.cart_service import CartService
from app.buyer.dtos.requests.add_to_cart_request import AddToCartRequest
from app.buyer.dtos.requests.checkout_request import CheckoutRequest
from app.shared.exceptions.custom_errors import ValidationError

cart_bp = Blueprint("cart_bp", __name__, url_prefix="/buyer/cart")

def _get_buyer_id():
    user = getattr(g, "user", None)
    if not user:
        raise ValidationError("Missing authenticated user.")
    return user.get("user_id")

@cart_bp.route("/add", methods=["POST"])
@token_required
@role_required("buyer")
def add_to_cart():
    buyer_id = _get_buyer_id()
    data = request.get_json(force=True) or {}
    req = AddToCartRequest(artwork_id=data.get("artwork_id"), quantity=data.get("quantity", 1))
    service = CartService(CartRepository(), ArtworkRepository())
    resp = service.add_to_cart(buyer_id, req)
    return jsonify(resp.to_dict()), 201

@cart_bp.route("/", methods=["GET"])
@token_required
@role_required("buyer")
def get_cart():
    buyer_id = _get_buyer_id()
    service = CartService(CartRepository(), ArtworkRepository())
    resp = service.get_cart(buyer_id)
    return jsonify(resp), 200

@cart_bp.route("/checkout", methods=["POST"])
@token_required
@role_required("buyer")
def checkout():
    data = request.get_json(force=True) or {}
    req = CheckoutRequest(cart_id=data.get("cart_id"), payment_method_id=data.get("payment_method_id"))
    service = CartService(CartRepository(), ArtworkRepository())
    resp = service.checkout(req)
    return jsonify(resp), 200
