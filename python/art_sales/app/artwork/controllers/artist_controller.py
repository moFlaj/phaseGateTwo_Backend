# app/artist/routes/artist_controller.py
from flask import Blueprint, request, jsonify, g
from app.utilities.jwt_utils import token_required, role_required
from app.artist.services.artist_service import ArtistService
from app.artist.persistence.artwork_repository import ArtworkRepository
from app.artist.dtos.requests.artwork_request import ArtworkRequest
from app.shared.exceptions.custom_errors import ValidationError, OrderNotFoundError, UnauthorizedOrderActionError
from app.artist.services.s3_service import S3Service
from app.buyer.persistence.order_repository import OrderRepository
from app.buyer.services.order_service import OrderService

artist_bp = Blueprint("artist_bp", __name__, url_prefix="/artist")


def _get_artist_id() -> str:
    # token_required sets g.user with 'user_id' and 'role'
    user = getattr(g, "user", None)
    if not user:
        raise ValidationError("Missing authenticated user.")
    return user.get("user_id")


@artist_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("artist")
def dashboard():
    artist_id = _get_artist_id()
    service = ArtistService(ArtworkRepository())
    summary = service.artist_summary(artist_id)
    return jsonify({
        "success": True,
        "summary": summary
    }), 200


@artist_bp.route("/works", methods=["GET"])
@token_required
@role_required("artist")
def list_works():
    artist_id = _get_artist_id()
    # optional pagination
    try:
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
    except Exception:
        return jsonify({"success": False, "message": "Invalid pagination parameters."}), 400

    service = ArtistService(ArtworkRepository())
    docs = service.list_artworks(artist_id, limit=limit, skip=skip)
    return jsonify({"success": True, "artworks": docs}), 200


@artist_bp.route("/works", methods=["POST"])
@token_required
@role_required("artist")
def create_work():
    artist_id = _get_artist_id()
    data = request.get_json(force=True) or {}
    req = ArtworkRequest(
        title=data.get("title"),
        price=data.get("price", 0),
        medium=data.get("medium"),
        dimensions=data.get("dimensions"),
        description=data.get("description"),
        is_original=data.get("is_original", True),
        variants=data.get("variants"),
        s3_key=data.get("s3_key"),
    )
    try:
        service = ArtistService(ArtworkRepository())
        resp = service.create_artwork(artist_id, req)
        return jsonify(resp.to_dict()), 201
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Failed to create artwork."}), 500


@artist_bp.route("/works/<artwork_id>", methods=["GET"])
@token_required
@role_required("artist")
def get_work(artwork_id: str):
    artist_id = _get_artist_id()
    try:
        service = ArtistService(ArtworkRepository())
        resp = service.get_artwork(artist_id, artwork_id)
        resp["success"] = True
        return jsonify(resp), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 404


@artist_bp.route("/works/<artwork_id>", methods=["PUT"])
@token_required
@role_required("artist")
def update_work(artwork_id: str):
    artist_id = _get_artist_id()
    data = request.get_json(force=True) or {}
    # Only allow whitelisted update fields
    allowed = {"title", "price", "medium", "dimensions", "description", "is_original", "variants"}
    updates = {k: v for k, v in data.items() if k in allowed}
    try:
        service = ArtistService(ArtworkRepository())
        resp = service.update_artwork(artist_id, artwork_id, updates)
        return jsonify(resp.to_dict()), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400


@artist_bp.route("/works/<artwork_id>", methods=["DELETE"])
@token_required
@role_required("artist")
def delete_work(artwork_id: str):
    try:
        service = ArtistService(ArtworkRepository())
        resp = service.delete_artwork(artwork_id)
        return jsonify(resp.to_dict()), 200
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 404



@artist_bp.route("/works/upload-url", methods=["GET"])
@token_required
@role_required("artist")
def generate_upload_url():
    """Return a pre-signed S3 URL so artist can upload image directly."""
    filename = request.args.get("filename")
    if not filename:
        return jsonify({"success": False, "message": "Missing filename"}), 400

    s3_service = S3Service()
    try:
        result = s3_service.generate_upload_url(filename)
        return jsonify({"success": True, **result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

##can't upload happen in the backend?

@artist_bp.route("/orders/<order_id>/complete", methods=["PUT"])
@token_required
@role_required("artist")
def complete_order(order_id):
    artist_id = _get_artist_id()
    try:
        service = OrderService(OrderRepository())
        result = service.complete_order(order_id, artist_id)
        return jsonify(result), 200
    except OrderNotFoundError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except UnauthorizedOrderActionError as e:
        return jsonify({"success": False, "message": str(e)}), 403
    except ValidationError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": "Order completion failed."}), 500