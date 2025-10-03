# app/routes/buyer_controller.py
from flask import Blueprint, jsonify, request, g
from app.utilities.jwt_utils import token_required, role_required
from app.services.buyer_service import BuyerService
from app.persistence.buyer_repository import BuyerRepository
from app.dtos.requests.buyer_update_profile_request import BuyerUpdateProfileRequest
from app.dtos.requests.cart_item_request import CartItemRequest

buyer_bp = Blueprint("buyer", __name__, url_prefix="/buyer")
buyer_service = BuyerService(BuyerRepository())

@buyer_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("buyer")
def dashboard():
    response = buyer_service.get_order_history(g.user["user_id"])
    return jsonify(response.__dict__), 200

@buyer_bp.route("/profile", methods=["PUT"])
@token_required
@role_required("buyer")
def update_profile():
    data = request.json
    request_dto = BuyerUpdateProfileRequest(**data)
    response = buyer_service.update_profile(g.user["user_id"], request_dto)
    return jsonify(response), 200

@buyer_bp.route("/cart", methods=["POST"])
@token_required
@role_required("buyer")
def add_to_cart():
    data = request.json
    request_dto = CartItemRequest(**data)
    response = buyer_service.add_to_cart(g.user["user_id"], request_dto)
    return jsonify(response), 201

@buyer_bp.route("/cart", methods=["GET"])
@token_required
@role_required("buyer")
def get_cart():
    response = buyer_service.get_cart(g.user["user_id"])
    return jsonify(response), 200
