from flask import jsonify

from app.exceptions.custom_exceptions import ValidationException, ResourceExistsException


def register_error_handlers(app):
    @app.errorhandler(ValidationException)
    def handle_validation_exception(e):
        response = jsonify({"success": False, "message": str(e)})
        response.status_code = 400  # Bad Request
        return response

    @app.errorhandler(ResourceExistsException)
    def handle_resource_exists_exception(e):
        response = jsonify({"success": False, "message": str(e)})
        response.status_code = 409  # Conflict
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        print("Unhandled Exception:", e)  # 👈 add this line temporarily
        response = jsonify({"success": False, "message": "An unexpected error occurred."})
        response.status_code = 500
        return response

