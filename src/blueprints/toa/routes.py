from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from src.app.extensions import services
from src.utils.decorators import require_token_and_json

toa_bp = Blueprint("toa", __name__, url_prefix="/toa")

# Route Constants
MAIN_WELCOME_ROUTE = "main.welcome"
MAIN_LOGIN_ROUTE = "main.login"
TOA_MANAGE_TECNICOS_ROUTE = "toa.manage_tecnicos"
TOA_LIST_TECNICOS_ROUTE = "toa.list_tecnicos"
TOA_MANAGE_COMENTARIOS_ROUTE = "toa.manage_comentarios"


def _handle_route_error(e, error_route=MAIN_WELCOME_ROUTE, route_name="route"):
    """
    Common error handling for routes.
 
    Args:
        e: Exception object
        error_route: Route to redirect to on error
        route_name: Name of the route for logging
    """
    if isinstance(e, ValueError):
        flash(str(e), "error")
        return redirect(url_for(error_route))
    elif isinstance(e, RuntimeError):
        flash("Error del sistema. Inténtelo de nuevo.", "error")
        return redirect(url_for(error_route))
    else:
        print(f"Unexpected error in {route_name}: {str(e)}")
        flash("Error inesperado. Inténtelo de nuevo.", "error")
        return redirect(url_for(error_route))


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
@login_required
def manage_comentarios(codigo_orden_trabajo):
    """
    Manage comentarios for a specific orden de trabajo.

    GET: Returns HTML page with form and existing comments (web UI)
    POST: Adds a new comment and redirects (web form submission)

    Authentication: Flask-Login @login_required decorator
    """

    try:
        if request.method == "POST":
            # Handle form submission
            comentario_data = {
                "comentario": request.form.get("comentario", ""),
                "num_ticket": request.form.get("num_ticket", ""),
            }

            # Add comment through use case
            services.comentarios_use_case.add_comentario(
                user=current_user,
                codigo_orden_trabajo=codigo_orden_trabajo,
                comentario_data=comentario_data,
            )

            flash("Comentario agregado exitosamente", "success")
            return redirect(
                url_for(
                    TOA_MANAGE_COMENTARIOS_ROUTE,
                    codigo_orden_trabajo=codigo_orden_trabajo,
                )
            )

        else:
            # GET: Show form and comments count (optimized - only get count)
            data = services.comentarios_use_case.get_comentarios_count_for_orden(
                user=current_user,
                codigo_orden_trabajo=codigo_orden_trabajo,
            )

            # Convert data for template
            orden_trabajo = type("OrdenTrabajo", (), data["orden_trabajo"])

            return render_template(
                "add_comentario.html",
                username=current_user.username,
                orden_trabajo=orden_trabajo,
                comentarios_count=data["comentarios_count"],
            )

    except ValueError as e:
        # Special handling for orden not found/access denied errors
        if "no encontrada o el usuario no tiene acceso" in str(e):
            flash(str(e), "error")
            return render_template(
                "add_comentario.html",
                username=current_user.username,
                orden_trabajo=type(
                    "OrdenTrabajo", (), {"codigo": codigo_orden_trabajo}
                ),
                comentarios_count=0,
                error_state=True,
            )
        # For other ValueError, use common error handling
        return _handle_route_error(e, MAIN_WELCOME_ROUTE, "manage_comentarios")

    except Exception as e:
        return _handle_route_error(e, MAIN_WELCOME_ROUTE, "manage_comentarios")


@toa_bp.route("/tecnicos", methods=["GET", "POST"])
@login_required
def manage_tecnicos():
    """Route for managing técnicos and supervisores."""

    try:
        if request.method == "POST":
            # Get form data - expect multiple tecnicos
            tecnicos_data = []

            # Parse form data to get multiple tecnicos
            form_data = request.form.to_dict(flat=False)

            # Count how many tecnicos were submitted
            max_index = 0
            for key in form_data.keys():
                if key.startswith("nombre_tecnico_"):
                    index = int(key.split("_")[-1])
                    max_index = max(max_index, index)

            # Collect data for each tecnico
            for i in range(max_index + 1):
                nombre_tecnico = request.form.get(f"nombre_tecnico_{i}", "").strip()
                rut_tecnico = request.form.get(f"rut_tecnico_{i}", "").strip()

                # Only include if both fields have data
                if nombre_tecnico and rut_tecnico:
                    nombre_supervisor = request.form.get(
                        "nombre_supervisor", ""
                    ).strip()

                    tecnicos_data.append(
                        {
                            "nombre_tecnico": nombre_tecnico,
                            "rut_tecnico": rut_tecnico,
                            "nombre_supervisor": nombre_supervisor,
                        }
                    )

            if not tecnicos_data:
                flash("Debe agregar al menos un técnico.", "error")
                return redirect(url_for(TOA_MANAGE_TECNICOS_ROUTE))

            # Add tecnicos using the use case
            result = services.tecnico_supervisor_use_case.add_tecnicos_supervisores(
                user=current_user,
                tecnicos_data=tecnicos_data,
            )

            flash(result["message"], "success")
            return redirect(url_for(TOA_MANAGE_TECNICOS_ROUTE))

        else:
            # GET request - show form only
            data = services.tecnico_supervisor_use_case.get_tecnicos_for_user_empresa(
                user=current_user
            )

            return render_template(
                "manage_tecnicos.html",
                username=current_user.username,
                empresa_nombre=data["empresa_nombre"],
            )

    except Exception as e:
        return _handle_route_error(e, TOA_MANAGE_TECNICOS_ROUTE, "manage_tecnicos")


@toa_bp.route("/tecnicos/lista", methods=["GET"])
@login_required
def list_tecnicos():
    """Route for viewing the list of técnicos for the user's empresa."""
    try:
        # Get tecnicos data for the user's empresa
        data = services.tecnico_supervisor_use_case.get_tecnicos_for_user_empresa(
            user=current_user
        )

        return render_template(
            "list_tecnicos.html",
            username=current_user.username,
            empresa_nombre=data["empresa_nombre"],
            tecnicos=data["tecnicos"],
        )

    except Exception as e:
        return _handle_route_error(e, MAIN_WELCOME_ROUTE, "list_tecnicos")
