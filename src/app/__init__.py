from flask import Flask
import os
import time

from src.app.extensions import login_manager, services
from src.config import Config
from src.models import db, migrate


def create_app() -> Flask:
    """Application factory pattern"""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Load configuration
    app.config.from_object(Config)

    # Set process timezone (defaults to America/Santiago, can be overridden via APP_TIMEZONE)
    timezone_name = os.environ.get("APP_TIMEZONE", "America/Santiago")
    os.environ["TZ"] = timezone_name
    if hasattr(time, "tzset"):
        time.tzset()

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    services.init_app(app)

    # Register blueprints
    from src.blueprints.main import main_bp
    from src.blueprints.toa import toa_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(toa_bp)

    return app
