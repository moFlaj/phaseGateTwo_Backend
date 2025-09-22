from flask import Blueprint, request, jsonify
from app.dtos.requests.user_signup_request import UserSignupRequest
from app.services.auth_services import AuthService
from app.persistence.user_repository import UserRepository
from app.utilities.password_hasher import PasswordHasher

# Dependency setup
user_repository = UserRepository()
password_hasher = PasswordHasher()
auth_service = AuthService(user_repository, password_hasher)

# Flask Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json

    try:
        signup_request = UserSignupRequest(**data)
        response = auth_service.signup_user(signup_request)
        status_code = 201 if response.success else 400
        return jsonify(response.__dict__), status_code

    except TypeError as te:
        return jsonify({
            "success": False,
            "message": f"Invalid request payload: {str(te)}"
        }), 400
