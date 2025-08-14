import base64
import os
from functools import wraps

from flask import current_app, flash, jsonify, redirect, request, url_for
from flask_login import current_user


def require_token(expected_token: str = None):
    """
    Decorator to validate authentication token from request headers.

    Args:
        expected_token: The expected token value (defaults to API_TOKEN from config)

    Returns:
        Decorator function that validates the token before executing the route

    Usage:
        @require_token()
        def my_route():
            return "Success"

        @require_token("custom-token")
        def my_other_route():
            return "Success"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get expected token from config if not provided
            token_to_check = expected_token or current_app.config.get(
                "API_TOKEN", "1234567890"
            )

            # Get token from headers
            token = request.headers.get("Token")

            # Check if token is provided
            if not token:
                return jsonify({"error": "Se requiere el header de token"}), 401

            # Validate token
            if token != token_to_check:
                return jsonify({"error": "Token de autenticación inválido"}), 401

            # Token is valid, proceed with the original function
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_json():
    """
    Decorator to ensure request has JSON content type and valid JSON data.

    Usage:
        @require_json()
        def my_route():
            data = request.get_json()  # This will be guaranteed to exist
            return "Success"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate Content-Type
            if not request.is_json:
                return jsonify({"error": "Content-Type debe ser application/json"}), 400

            # Validate JSON data exists
            json_data = request.get_json()
            if json_data is None:
                return jsonify({"error": "Datos JSON inválidos o faltantes"}), 400

            # JSON is valid, proceed with the original function
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_token_and_json(expected_token: str = None):
    """
    Combined decorator that requires both valid token and JSON data.

    Args:
        expected_token: The expected token value (defaults to API_TOKEN from config)

    Usage:
        @require_token_and_json()
        def my_route():
            data = request.get_json()
            return "Success"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate Content-Type
            if not request.is_json:
                return jsonify({"error": "Content-Type debe ser application/json"}), 400

            # Get expected token from config if not provided
            token_to_check = expected_token or current_app.config.get(
                "API_TOKEN", "1234567890"
            )

            # Get and validate token from headers
            token = request.headers.get("Token")
            if not token:
                return jsonify({"error": "Se requiere el header de token"}), 401

            if token != token_to_check:
                return jsonify({"error": "Token de autenticación inválido"}), 401

            # Validate JSON data
            json_data = request.get_json()
            if json_data is None:
                return jsonify({"error": "Datos JSON inválidos o faltantes"}), 400

            # All validations passed, proceed with the original function
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def dev_only(redirect_route: str = "main.welcome"):
    """
    Decorator to restrict access to the 'dev' user only.

    Args:
        redirect_route: Route to redirect to if access is denied

    Usage:
        @dev_only()
        def admin_function():
            return "Dev only content"
        @dev_only("main.login")
        def other_admin_function():
            return "Dev only content"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash("Debe iniciar sesión para acceder a esta página", "error")
                return redirect(url_for("main.login"))

            # Check if user is 'dev'
            if current_user.username != "dev":
                flash(
                    "Acceso denegado. Solo el usuario 'dev' puede acceder a esta página",
                    "error",
                )
                return redirect(url_for(redirect_route))

            # User is dev, proceed with the original function
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_basic_auth(username: str = None, password: str = None):
    """
    Decorator to require HTTP Basic Authentication.

    Args:
        username: Expected username (defaults to BASIC_AUTH_USERNAME from config/env)
        password: Expected password (defaults to BASIC_AUTH_PASSWORD from config/env)

    Usage:
        @require_basic_auth()
        def protected_route():
            return "Protected content"

        @require_basic_auth("admin", "secret")
        def custom_auth_route():
            return "Custom auth content"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get credentials from config or environment if not provided
            expected_username = (
                username
                or current_app.config.get("BASIC_AUTH_USERNAME")
                or os.getenv("BASIC_AUTH_USERNAME")
            )
            expected_password = (
                password
                or current_app.config.get("BASIC_AUTH_PASSWORD")
                or os.getenv("BASIC_AUTH_PASSWORD")
            )

            if not expected_username or not expected_password:
                return jsonify({"error": "Basic auth credentials not configured"}), 500

            # Get Authorization header
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Basic "):
                response = jsonify({"error": "Authentication required"})
                response.headers["WWW-Authenticate"] = 'Basic realm="Login Required"'
                return response, 401

            try:
                # Decode base64 credentials
                encoded_credentials = auth_header.split(" ")[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode(
                    "utf-8"
                )
                provided_username, provided_password = decoded_credentials.split(":", 1)

                # Verify credentials
                if (
                    provided_username != expected_username
                    or provided_password != expected_password
                ):
                    response = jsonify({"error": "Invalid credentials"})
                    response.headers["WWW-Authenticate"] = (
                        'Basic realm="Login Required"'
                    )
                    return response, 401

            except (ValueError, UnicodeDecodeError):
                response = jsonify({"error": "Invalid authorization header format"})
                response.headers["WWW-Authenticate"] = 'Basic realm="Login Required"'
                return response, 401

            # Authentication successful, proceed with the original function
            return f(*args, **kwargs)

        return decorated_function

    return decorator
