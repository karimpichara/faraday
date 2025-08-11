from functools import wraps

from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user


def require_token(expected_token: str = "1234567890"):
    """
    Decorator to validate authentication token from request headers.

    Args:
        expected_token: The expected token value (defaults to "1234567890")

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
            # Get token from headers
            token = request.headers.get("Token")

            # Check if token is provided
            if not token:
                return jsonify({"error": "Se requiere el header de token"}), 401

            # Validate token
            if token != expected_token:
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


def require_token_and_json(expected_token: str = "1234567890"):
    """
    Combined decorator that requires both valid token and JSON data.

    Args:
        expected_token: The expected token value (defaults to "1234567890")

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

            # Get and validate token from headers
            token = request.headers.get("Token")
            if not token:
                return jsonify({"error": "Se requiere el header de token"}), 401

            if token != expected_token:
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
