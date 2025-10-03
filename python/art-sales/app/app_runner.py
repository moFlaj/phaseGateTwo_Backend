# app/app_runner.py
from flask import Flask
from flask_cors import CORS

from app.config.db_config import DevConfig
from app.exceptions.global_error_handler import register_error_handlers
from app.extensions import mongo
from app.routes.auth_controller import auth_bp
from app.routes.artist_controller import artist_bp
from app.routes.buyer_controller import buyer_bp


def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    CORS(app, origins=["http://localhost:5500"])

    # Register routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(artist_bp)
    app.register_blueprint(buyer_bp)

    # Register error handlers
    register_error_handlers(app)

    return app

