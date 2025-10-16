# app/app_runner.py
from flask import Flask
from flask_cors import CORS
from app.shared.config.db_config import DevConfig
from app.shared.exceptions.global_error_handler import register_error_handlers
from app.extensions import mongo
from app.auth.controllers.auth_controller import auth_bp, init_services
from app.user.routes.artist_controller import artist_bp
from app.user.routes.paystack_webhook_controller import paystack_webhook_bp, init_services as init_paystack_services
import os

from app.user.routes.buyer_controller import buyer_bp
from app.user.routes.checkout_controller import checkout_bp
from app.user.routes.cart_controller import cart_bp
from app.wallet.controllers.wallet_controller import wallet_bp, init_wallet_service


def create_app(config_class=DevConfig):
    """Factory: create Flask app, initialize extensions and services.
    Important: do not import mailer implementations at module import time
that access
    the Flask application context. We instantiate mailers inside the app
context.
"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure CORS with specific settings to handle preflight requests properly
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:5000", "http://127.0.0.1:5501", "http://localhost:5501", "http://localhost:5502", "http://127.0.0.1:5502"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "X-User-ID"],
            "supports_credentials": True
        }
    })
    
    # Extensions
    mongo.init_app(app)
    # Decide which mailer to use. We import mailer classes *inside* the app context
    # to avoid circular imports/app context issues.
    use_mock = app.config.get("USE_MOCK_MAILER", False)

    if use_mock:
        from app.shared.utilities.email_service import MockMailer
        with app.app_context():
            mailer = MockMailer()
            init_services(mailer, async_email=False)
    else:
        # Build SMTP mailer using config values (safe inside app context)
        from app.shared.utilities.email_service import SMTPMailer
        smtp_kwargs = {
            "smtp_host": app.config.get("SMTP_HOST"),
            "smtp_port": app.config.get("SMTP_PORT"),
            "username": app.config.get("SMTP_USERNAME"),
            "password": app.config.get("SMTP_PASSWORD"),
            "from_addr": app.config.get("SMTP_FROM") or app.config.get("MAIL_DEFAULT_SENDER")
        }
    # Remove None values so SMTPMailer will fall back to env vars if necessary
        smtp_kwargs = {k: v for k, v in smtp_kwargs.items() if v is not None}
        with app.app_context():
            mailer = SMTPMailer(**smtp_kwargs)
            init_services(mailer, async_email=app.config.get("ASYNC_EMAIL", False))

    # Initialize wallet service
    with app.app_context():
        init_wallet_service()
        
    # Initialize Paystack webhook service
    with app.app_context():
        init_paystack_services(app.config.get("EMAIL_SERVICE"))

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(artist_bp, url_prefix='/api/artist')
    app.register_blueprint(buyer_bp, url_prefix='/api/buyer')
    app.register_blueprint(checkout_bp, url_prefix='/api/checkout')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
    app.register_blueprint(paystack_webhook_bp, url_prefix='/api/paystack')


    # Error handlers
    register_error_handlers(app)
    return app


run_app = create_app()

if __name__ == "__main__":
    run_app.run(host="127.0.0.1", port=5000, debug=True)