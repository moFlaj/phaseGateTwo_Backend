#app/exceptions/global_error_handler
from flask import jsonify


from app.shared.exceptions.custom_errors import (
    ValidationError,
    ResourceExistsError,
    InvalidVerificationCodeError,
    MailerSendError, NotFoundError, UserAlreadyExistsError,
)


def register_error_handlers(app):
    # More specific handlers first
    @app.errorhandler(UserAlreadyExistsError)
    def handle_user_already_exists(e):
        return jsonify({"success": False, "message": str(e)}), 404

    @app.errorhandler(ResourceExistsError)
    def handle_user_exists(e):
        return jsonify({"success": False, "message": str(e)}), 409

    @app.errorhandler(NotFoundError)
    def handle_verification_not_found(e):
        return jsonify({"success": False, "message": str(e)}), 404

    @app.errorhandler(InvalidVerificationCodeError)
    def handle_invalid_code(e):
        return jsonify({"success": False, "message": str(e)}), 400

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"success": False, "message": str(e)}), 400

    @app.errorhandler(MailerSendError)
    def handle_mailer_error(e):
        return jsonify({"success": False, "message": str(e)}), 500

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        print("Unhandled Exception:", e)
        return jsonify({"success": False, "message": "An unexpected error occurred."}), 500