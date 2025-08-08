from flask import Flask

from src.app.extensions import services
from src.config import Config
from src.models import db, migrate


def create_app() -> Flask:
    """Application factory pattern"""
    app = Flask(
        __name__, static_folder="src/app/static", template_folder="src/app/templates"
    )

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    services.init_app(app)

    # Register blueprints
    from src.blueprints.main import main_bp
    from src.blueprints.toa import toa_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(toa_bp)

    return app
