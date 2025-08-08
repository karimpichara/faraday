from flask import (
    Blueprint,
    jsonify,
    request,
    flash,
    redirect,
    render_template,
    session,
    url_for,
)

from src.app.extensions import services
from src.utils.decorators import require_token_and_json
from src.models.auth.user import User

toa_bp = Blueprint("toa", __name__, url_prefix="/toa")

# Constants
MAIN_WELCOME_ROUTE = "main.welcome"


@toa_bp.route("/healthcheck")
def healthcheck():
    return jsonify({"status": "ok"})


def _validate_file_upload():
    """Common validation logic for file uploads"""
    if "file" not in request.files:
        return jsonify({"error": "No se proporcionó archivo"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó archivo"}), 400

    if not file.filename.endswith(".json"):
        return jsonify({"error": "El archivo debe ser un archivo JSON"}), 400

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
                    "error": f"Zona inválida '{zone}'. Las zonas válidas son: {', '.join(valid_zones)}"
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
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@toa_bp.route("/comentarios/<codigo_orden_trabajo>", methods=["GET", "POST"])
def manage_comentarios(codigo_orden_trabajo):
    """
    Manage comentarios for a specific orden de trabajo.

    GET: Returns HTML page with form and existing comments (web UI)
    POST: Adds a new comment and redirects (web form submission)

    Authentication: Session-based (for web UI)
    """

    # Check authentication
    if "username" not in session:
        return redirect(url_for("main.login", next=request.url))

    # Get current user
    user = User.get_by_username(session["username"])
    if not user:
        session.pop("username", None)
        flash("Usuario no encontrado", "error")
        return redirect(url_for("main.login"))

    try:
        if request.method == "POST":
            # Handle form submission
            comentario_data = {
                "comentario": request.form.get("comentario", ""),
                "num_ticket": request.form.get("num_ticket", ""),
            }

            # Add comment through use case
            services.comentarios_use_case.add_comentario(
                user=user,
                codigo_orden_trabajo=codigo_orden_trabajo,
                comentario_data=comentario_data,
            )

            flash("Comentario agregado exitosamente", "success")
            return redirect(
                url_for(
                    "toa.manage_comentarios", codigo_orden_trabajo=codigo_orden_trabajo
                )
            )

        else:
            # GET: Show form and comments count (optimized - only get count)
            data = services.comentarios_use_case.get_comentarios_count_for_orden(
                user=user,
                codigo_orden_trabajo=codigo_orden_trabajo,
            )

            # Convert data for template
            orden_trabajo = type("OrdenTrabajo", (), data["orden_trabajo"])

            return render_template(
                "add_comentario.html",
                username=session["username"],
                orden_trabajo=orden_trabajo,
                comentarios_count=data["comentarios_count"],
            )

    except ValueError as e:
        # Validation errors (user doesn't have access, orden not found, etc.)
        flash(str(e), "error")

        # For orden not found or access denied errors, create a minimal context to show the error page
        if "no encontrada o el usuario no tiene acceso" in str(e):
            return render_template(
                "add_comentario.html",
                username=session["username"],
                orden_trabajo=type(
                    "OrdenTrabajo", (), {"codigo": codigo_orden_trabajo}
                ),
                comentarios_count=0,
                error_state=True,
            )
        else:
            # For access denied errors, redirect to welcome
            return redirect(url_for(MAIN_WELCOME_ROUTE))

    except RuntimeError:
        # Database or system errors
        flash("Error del sistema. Inténtelo de nuevo.", "error")
        return redirect(url_for(MAIN_WELCOME_ROUTE))

    except Exception:
        # Unexpected errors
        flash("Error inesperado. Inténtelo de nuevo.", "error")
        return redirect(url_for(MAIN_WELCOME_ROUTE))
