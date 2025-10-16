# app/buyer/routes/buyer_controller.py
from flask import Blueprint, request, jsonify, g
from app.shared.utilities.jwt_utils import token_required, role_required
from app.user.services.order_service import OrderService
from app.user.persistence.order_repository import OrderRepository
from app.user.dtos.requests.create_order_request import CreateOrderRequest
from app.shared.exceptions.custom_errors import (
    ValidationError, 
    ArtworkNotFoundError, 
    OrderAlreadyExistsError,
    OrderNotFoundError,
    UnauthorizedOrderActionError
)
from app.user.persistence.artwork_repository import ArtworkRepository
from app.user.services.buyer_service import BuyerService
from app.user.services.s3_service import S3Service


buyer_bp = Blueprint("buyer_bp", __name__, url_prefix="/buyer")

def _get_buyer_id():
    user = getattr(g, "user", None)
    if not user:
        raise ValidationError("Missing authenticated user.")
    return user.get("user_id")

@buyer_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("buyer")
def buyer_dashboard():
    buyer_id = _get_buyer_id()
    service = BuyerService(OrderRepository())
    summary = service.buyer_summary(buyer_id)
    return jsonify({"success": True, "message": "Buyer dashboard", "summary": summary}), 200


@buyer_bp.route("/orders", methods=["POST"])
@token_required
@role_required("buyer")
def create_order():
    buyer_id = _get_buyer_id()
    data = request.get_json(force=True) or {}
    req = CreateOrderRequest(
        artwork_id=data.get("artwork_id"),
        quantity=data.get("quantity", 1),
        shipping_address=data.get("shipping_address")
    )
    try:
        service = OrderService(OrderRepository())
        resp = service.create_order(buyer_id, req)
        return jsonify(resp.to_dict()), 201
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except ArtworkNotFoundError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except OrderAlreadyExistsError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Order creation failed."}), 500


@buyer_bp.route("/orders", methods=["GET"])
@token_required
@role_required("buyer")
def list_orders():
    buyer_id = _get_buyer_id()
    try:
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
    except Exception:
        return jsonify({"success": False, "message": "Invalid pagination params."}), 400
    service = OrderService(OrderRepository())
    docs = service.list_orders_by_buyer(buyer_id, limit=limit, skip=skip)
    return jsonify({"success": True, "orders": docs}), 200


@buyer_bp.route("/orders/<order_id>/confirm", methods=["POST"])
@token_required
@role_required("buyer")
def confirm_order_receipt(order_id):
    """Buyer confirms receipt of artwork."""
    buyer_id = _get_buyer_id()
    try:
        service = OrderService(OrderRepository())
        result = service.confirm_receipt(order_id, buyer_id)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Order confirmation failed."}), 500


@buyer_bp.route("/search", methods=["GET"])
@token_required
@role_required("buyer")
def search_artworks():
    """
    Query params:
      q - text query (optional)
      min_price - min price filter (optional)
      max_price - max price filter (optional)
      limit - page size (optional)
      skip - offset (optional)
    """
    q = request.args.get("q")
    min_price = request.args.get("min_price", 0.0)
    max_price = request.args.get("max_price", 1000000.0)
    limit = request.args.get("limit", 50)
    skip = request.args.get("skip", 0)

    try:
        service = BuyerService(OrderRepository(), ArtworkRepository())
        results = service.search_artworks(query=q, min_price=min_price, max_price=max_price, limit=limit, skip=skip)
        return jsonify({"success": True, "results": results}), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        # Let global error handler catch domain errors; otherwise return 500
        print("Search error:", e)
        return jsonify({"success": False, "message": "Failed to search artworks."}), 500


@buyer_bp.route("/artworks/<artwork_id>", methods=["GET"])
def view_artwork(artwork_id):
    """Public endpoint to view an artwork with image URL."""
    try:
        # Get artwork from repository
        repo = ArtworkRepository()
        artwork = repo.find_by_id(artwork_id)
        
        if not artwork:
            return jsonify({"success": False, "message": "Artwork not found"}), 404
            
        # Add image URL if S3 key exists
        s3_key = artwork.get("s3_key")
        if s3_key:
            s3_service = S3Service()
            try:
                artwork["image_url"] = s3_service.generate_get_url(s3_key, expires_in=3600)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to generate image URL: {e}")
        
        # Format response
        artwork["artwork_id"] = str(artwork.pop("_id"))
        return jsonify({"success": True, "artwork": artwork}), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to retrieve artwork"}), 500