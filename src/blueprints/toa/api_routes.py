"""
API routes for TOA blueprint that use Basic Authentication.
These routes are typically used by external systems like PowerBI.
"""

import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    send_file,
)

from src.app.extensions import services
from src.utils.decorators import require_basic_auth
from src.utils.image_utils import serve_default_placeholder_image

# Create API blueprint with same /toa prefix to maintain URL compatibility
toa_api_bp = Blueprint("toa_api", __name__)


@toa_api_bp.route("/toa/get_empresas_externas", methods=["GET"])
@require_basic_auth()
def get_empresas_externas_toa():
    """
    Get all EmpresasExternasToa records.

    Returns:
        JSON list of companies with nombre, nombre_toa, and rut fields
    """
    try:
        result = services.empresas_externas_use_case.get_empresas_externas_toa_all()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@toa_api_bp.route("/toa/comentarios", methods=["GET"])
@require_basic_auth()
def get_all_comentarios():
    """
    Get all comentarios from the system.

    Headers:
        Authorization: Basic Auth credentials

    Returns:
        JSON response with all comentarios data including:
        - comentarios: List of all comentarios with full details
        - total: Total number of comentarios
    """
    try:
        # Get all comentarios through use case (no token needed, already validated)
        result = services.comentarios_use_case.get_all_comentarios()
        return jsonify(result), 200

    except RuntimeError as e:
        # Database or system errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@toa_api_bp.route("/toa/ordenes_trabajo", methods=["GET"])
@require_basic_auth()
def get_all_ordenes_trabajo():
    """
    Get all ordenes de trabajo from the system.

    Headers:
        Authorization: Basic Auth credentials

    Returns:
        JSON response with all ordenes de trabajo data including:
        - ordenes_trabajo: List of all records with details
        - total: Total number of records
    """
    try:
        # Get all ordenes de trabajo through use case (no token needed, already validated)
        result = services.orden_trabajo_use_case.get_all_ordenes_trabajo()
        return jsonify(result), 200

    except RuntimeError as e:
        # Database or system errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@toa_api_bp.route("/toa/users", methods=["GET"])
@require_basic_auth()
def get_all_users():
    """
    Get all users from the system.

    Headers:
        Authorization: Basic Auth credentials

    Returns:
        JSON response with all users data including:
        - users: List of all active users with details
        - total: Total number of users
    """
    try:
        # Get all users through use case (no token needed, already validated)
        result = services.user_use_case.get_all_users_data()

        # Rename the key to match the pattern of other endpoints
        result["users"] = result.pop("users")  # Keep the same key

        return jsonify(result), 200

    except RuntimeError as e:
        # Database or system errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@toa_api_bp.route("/toa/powerbi/comentarios/imagen/<int:comentario_id>")
@require_basic_auth()
def serve_comentario_image_powerbi(comentario_id):
    """
    PowerBI-specific endpoint to serve images for comentarios.
    Always returns an image - either the actual image or a default placeholder.
    Uses Basic Authentication instead of session-based auth.
    """
    try:
        # Get the comentario
        comentario = services.comentarios.get_comentario_by_id(comentario_id)

        # If comentario doesn't exist or has no image, return default placeholder
        if not comentario or not comentario.imagen_path:
            return serve_default_placeholder_image()

        # Build the full image path
        from src.constants import ROOT_PATH

        if os.path.isabs(comentario.imagen_path):
            full_image_path = comentario.imagen_path
        else:
            full_image_path = os.path.join(ROOT_PATH, comentario.imagen_path)

        # If image file doesn't exist, return placeholder
        if not os.path.exists(full_image_path):
            current_app.logger.warning(
                f"PowerBI: Image file not found for comentario {comentario_id}: {full_image_path}"
            )
            return serve_default_placeholder_image()

        # Log successful access for monitoring
        current_app.logger.info(
            f"PowerBI: Serving image for comentario {comentario_id}"
        )

        return send_file(full_image_path)

    except Exception as e:
        # Log error and return placeholder instead of 404
        current_app.logger.error(
            f"PowerBI: Error serving image for comentario {comentario_id}: {str(e)}"
        )
        return serve_default_placeholder_image()


@toa_api_bp.route("/toa/tecnicos_supervisores", methods=["GET"])
@require_basic_auth()
def get_all_tecnicos_supervisores():
    """
    Get all tecnicos supervisores from the system.

    Headers:
        Authorization: Basic Auth credentials

    Returns:
        JSON response with all tecnicos supervisores data including:
        - tecnicos_supervisores: List of all tecnicos with full details
        - total: Total number of tecnicos supervisores
    """
    try:
        # Get all tecnicos supervisores through use case (no token needed, already validated)
        result = services.tecnico_supervisor_use_case.get_all_tecnicos_supervisores()
        return jsonify(result), 200

    except RuntimeError as e:
        # Database or system errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
