from flask import Flask


def create_app():
    """Application factory pattern"""
    app = Flask(
        __name__, static_folder="src/app/static", template_folder="src/app/templates"
    )

    # Configuration for sessions
    app.config["SECRET_KEY"] = "dev-secret-key-for-sessions"

    # Register blueprints
    from src.blueprints.main import main_bp

    app.register_blueprint(main_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5010)
