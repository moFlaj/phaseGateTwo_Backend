from flask import Flask
from app.extensions import mongo
from app.routes.auth_controller import auth_bp
from app.exceptions.global_error_handler import register_error_handlers

from app.config.db_config import DevConfig

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)

    app.register_blueprint(auth_bp)
    register_error_handlers(app)

    return app
