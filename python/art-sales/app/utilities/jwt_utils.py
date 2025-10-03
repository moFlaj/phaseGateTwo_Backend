# app/utilities/jwt_utils.py
import functools
from flask import request, jsonify, current_app, g
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

def token_required(fn):
    """
    Decorator to enforce JWT authentication.
    Extracts the token, validates it, and attaches the payload to `g.user`.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"success": False, "message": "Missing or invalid Authorization header"}), 401

        token = auth.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except (InvalidTokenError, Exception):
            return jsonify({"success": False, "message": "Invalid token"}), 401

        # Attach payload to request context
        g.user = {"user_id": payload.get("user_id"), "role": payload.get("role")}
        return fn(*args, **kwargs)
    return wrapper


def role_required(role):
    """
    Decorator to enforce role-based access control.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(g, "user", None):
                return jsonify({"success": False, "message": "Missing credentials"}), 401
            if g.user.get("role") != role:
                return jsonify({"success": False, "message": "Forbidden - insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
