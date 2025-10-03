# app/routes/artist_controller.py
from flask import Blueprint, jsonify, request, g
from app.utilities.jwt_utils import token_required, role_required
from app.services.artist_service import ArtistService
from app.persistence.artist_repository import ArtistRepository
from app.dtos.requests.artwork_upload_request import ArtworkUploadRequest

artist_bp = Blueprint("artist", __name__, url_prefix="/artist")
artist_service = ArtistService(ArtistRepository())

@artist_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("artist")
def dashboard():
    response = artist_service.get_dashboard(g.user["user_id"])
    return jsonify(response), 200

@artist_bp.route("/artwork", methods=["POST"])
@token_required
@role_required("artist")
def upload_artwork():
    data = request.json
    request_dto = ArtworkUploadRequest(**data)
    response = artist_service.upload_artwork(g.user["user_id"], request_dto)
    return jsonify(vars(response)), 201

@artist_bp.route("/artwork/<artwork_id>", methods=["PUT"])
@token_required
@role_required("artist")
def update_artwork(artwork_id):
    update_data = request.json
    response = artist_service.update_artwork(artwork_id, update_data)
    return jsonify(vars(response)), 200

@artist_bp.route("/artwork/<artwork_id>", methods=["DELETE"])
@token_required
@role_required("artist")
def delete_artwork(artwork_id):
    response = artist_service.delete_artwork(artwork_id)
    return jsonify(vars(response)), 200
