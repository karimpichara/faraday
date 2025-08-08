from flask import Blueprint, jsonify, request

from src.app.extensions import services
from src.utils.decorators import require_token_and_json

toa_bp = Blueprint("toa", __name__, url_prefix="/toa")


@toa_bp.route("/healthcheck")
def healthcheck():
    return jsonify({"status": "ok"})


def _validate_file_upload():
    """Common validation logic for file uploads"""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith(".json"):
        return jsonify({"error": "File must be a JSON file"}), 400

    return file, None


def _process_zone_file_upload(zone_method_name):
    """Common logic for processing zone file uploads"""
    try:
        file_or_error = _validate_file_upload()
        if len(file_or_error) == 2 and file_or_error[1] is not None:
            return file_or_error  # Return error response

        file = file_or_error[0]

        # Get the appropriate method from the initialized use case
        zone_method = getattr(services.historia_iniciados_use_case, zone_method_name)
        ot_no_ingresadas = zone_method(file)

        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "No ingresadas": ot_no_ingresadas,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Zone mapping for URL parameter to use case method
ZONE_MAPPING = {
    "south": "set_data_zona_sur",
    "north": "set_data_zona_norte",
    "center": "set_data_zona_centro",
    "metro": "set_data_zona_metropolitana",
    # Also support Spanish names for backward compatibility
    "sur": "set_data_zona_sur",
    "norte": "set_data_zona_norte",
    "centro": "set_data_zona_centro",
    "metropolitana": "set_data_zona_metropolitana",
}


@toa_bp.route("/set_data_toa_historia/<zone>", methods=["POST"])
def set_data_toa_historia_zone(zone):
    """
    Upload TOA historia data for a specific zone.

    Args:
        zone: Zone identifier (south, north, center, metro, sur, norte, centro, metropolitana)
    """
    # Validate zone parameter
    if zone not in ZONE_MAPPING:
        valid_zones = list(ZONE_MAPPING.keys())
        return (
            jsonify(
                {
                    "error": f"Invalid zone '{zone}'. Valid zones are: {', '.join(valid_zones)}"
                }
            ),
            400,
        )

    # Get the corresponding use case method name
    zone_method_name = ZONE_MAPPING[zone]
    return _process_zone_file_upload(zone_method_name)


# Backward compatibility routes - these will redirect to the new parameterized route
@toa_bp.route("/set_data_toa_historia_south_zone", methods=["POST"])
def set_data_toa_historia_south_zone():
    """Backward compatibility route"""
    return set_data_toa_historia_zone("south")


@toa_bp.route("/set_data_toa_historia_north_zone", methods=["POST"])
def set_data_toa_historia_north_zone():
    """Backward compatibility route"""
    return set_data_toa_historia_zone("north")


@toa_bp.route("/set_data_toa_historia_center_zone", methods=["POST"])
def set_data_toa_historia_center_zone():
    """Backward compatibility route"""
    return set_data_toa_historia_zone("center")


@toa_bp.route("/set_data_toa_historia_metro_zone", methods=["POST"])
def set_data_toa_historia_metropolitana_zone():
    """Backward compatibility route"""
    return set_data_toa_historia_zone("metro")


@toa_bp.route("/set_empresas_externas_toa", methods=["POST"])
def set_empresas_externas_toa():
    try:
        file_or_error = _validate_file_upload()
        if len(file_or_error) == 2 and file_or_error[1] is not None:
            return file_or_error  # Return error response

        file = file_or_error[0]

        services.empresas_externas_use_case.set_empresas_externas_toa(file)
        return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@toa_bp.route("/get_empresas_externas", methods=["GET"])
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


@toa_bp.route("/add_ordenes_trabajo", methods=["POST"])
@require_token_and_json()
def add_ordenes_trabajo():
    """
    Add multiple ordenes de trabajo to the database.

    Expected JSON format:
    [
        {"id_empresa": 5, "codigo": "1-abc123"},
        {"id_empresa": 6, "codigo": "3-abc128"}
    ]

    Headers:
        Token: Authentication token (default: "1234567890")
        Content-Type: application/json

    Returns:
        JSON response with operation results
    """
    try:
        # Get JSON data (guaranteed to exist due to decorator)
        ordenes_data = request.get_json()

        # Process the request through use case (no token needed, already validated)
        result = services.orden_trabajo_use_case.add_ordenes_trabajo(ordenes_data)
        return jsonify(result), 201

    except ValueError as e:
        # Validation errors (data format, business rules, etc.)
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        # Database or system errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
