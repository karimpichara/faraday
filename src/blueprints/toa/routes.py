import os

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required

from src.app.extensions import services
from src.utils.decorators import (
    require_basic_auth,
    require_token,
    require_token_and_json,
)
from src.utils.image_utils import serve_default_placeholder_image

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
        Token: Authentication token (configured via API_TOKEN env var)
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


@toa_bp.route("/comentarios", methods=["GET"])
@require_basic_auth()
def get_all_comentarios():
    """
    Get all comentarios from the system.

    Headers:
        Token: Authentication token (configured via API_TOKEN env var)

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


@toa_bp.route("/historia_ot_empresas", methods=["GET"])
@require_token()
def get_all_historia_ot_empresas():
    """
    Get all historia OT empresas from the system.

    Headers:
        Token: Authentication token (configured via API_TOKEN env var)

    Returns:
        JSON response with all historia OT empresas data including:
        - historia_ot_empresas: List of all records with full details
        - total: Total number of records
    """
    try:
        # Get all historia OT empresas through use case (no token needed, already validated)
        result = services.historia_iniciados_use_case.get_all_historia_ot_empresas()
        return jsonify(result), 200

    except RuntimeError as e:
        # Database or system errors
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # Unexpected errors
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


@toa_bp.route("/ordenes_trabajo", methods=["GET"])
@require_basic_auth()
def get_all_ordenes_trabajo():
    """
    Get all ordenes de trabajo from the system.

    Headers:
        Token: Authentication token (configured via API_TOKEN env var)

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


@toa_bp.route("/users", methods=["GET"])
@require_basic_auth()
def get_all_users():
    """
    Get all users from the system.

    Headers:
        Token: Authentication token (configured via API_TOKEN env var)

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

            # Get image file if provided
            imagen = request.files.get("imagen") if "imagen" in request.files else None

            # Add comment through use case
            services.comentarios_use_case.add_comentario(
                user=current_user,
                codigo_orden_trabajo=codigo_orden_trabajo,
                comentario_data=comentario_data,
                imagen=imagen,
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
            for key in form_data:
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


@toa_bp.route("/comentarios/imagen/<int:comentario_id>")
@login_required
def serve_comentario_image(comentario_id):
    """Serve image for a specific comentario."""
    try:
        # Get the comentario
        comentario = services.comentarios.get_comentario_by_id(comentario_id)
        if not comentario or not comentario.imagen_path:
            abort(404)

        # Verify user has access to the orden de trabajo
        if not comentario.orden_trabajo:
            abort(404)

        # Check if user is admin (dev user or has admin role)
        is_admin = current_user.username == "dev" or current_user.has_roles(["admin"])

        # Admin users have access to all images, regular users need validation
        if not is_admin:
            user_empresa_ids = [empresa.id for empresa in current_user.empresas]

            # Additional security: ensure user has at least one empresa assigned
            if not user_empresa_ids:
                # Log security event - user with no empresa assignments trying to access images
                current_app.logger.warning(
                    f"User {current_user.username} (ID: {current_user.id}) attempted to access "
                    f"image for comentario {comentario_id} but has no empresa assignments"
                )
                abort(403)  # User not assigned to any empresa

            if comentario.orden_trabajo.id_empresa not in user_empresa_ids:
                # Log potential unauthorized access attempt
                current_app.logger.warning(
                    f"User {current_user.username} (ID: {current_user.id}) attempted to access "
                    f"image for comentario {comentario_id} from empresa {comentario.orden_trabajo.id_empresa} "
                    f"but only has access to empresas: {user_empresa_ids}"
                )
                abort(403)  # Forbidden

        # Properly join the image path with the ROOT_PATH
        from src.constants import ROOT_PATH

        if os.path.isabs(comentario.imagen_path):
            # If it's already an absolute path, use it as is
            full_image_path = comentario.imagen_path
        else:
            # Join relative path with ROOT_PATH
            full_image_path = os.path.join(ROOT_PATH, comentario.imagen_path)

        # Check if image file exists
        if not os.path.exists(full_image_path):
            abort(404)

        return send_file(full_image_path)

    except Exception:
        abort(404)


@toa_bp.route("/powerbi/comentarios/imagen/<int:comentario_id>")
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


@toa_bp.route("/ordenes/comentarios", methods=["GET"])
@login_required
def list_ordenes_comentarios():
    """
    List ordenes de trabajo with pagination and search functionality.
    Users can search and select ordenes to view their comentarios.
    """
    try:
        # Get search parameters
        page = request.args.get("page", 1, type=int)
        search_codigo = request.args.get("codigo", "").strip()
        search_fecha_inicio = request.args.get("fecha_inicio", "").strip()
        search_fecha_fin = request.args.get("fecha_fin", "").strip()
        search_empresa_id = request.args.get("empresa_id", type=int)

        # Clear empty search parameters
        search_codigo = search_codigo if search_codigo else None
        search_fecha_inicio = search_fecha_inicio if search_fecha_inicio else None
        search_fecha_fin = search_fecha_fin if search_fecha_fin else None

        # Check if user is admin (dev user or has admin role)
        is_admin = current_user.username == "dev" or current_user.has_roles(["admin"])

        if is_admin:
            # Admin users see ALL ordenes and can filter by empresa
            result = services.orden_trabajo.get_ordenes_trabajo_admin(
                page=page,
                per_page=10,
                search_codigo=search_codigo,
                search_fecha_inicio=search_fecha_inicio,
                search_fecha_fin=search_fecha_fin,
                search_empresa_id=search_empresa_id,
            )
            # Get all empresas for admin filtering
            all_empresas = services.user.get_all_empresas()
        else:
            # Regular users see only their empresa's ordenes
            user_empresa_ids = [empresa.id for empresa in current_user.empresas]

            # Security check: ensure user has empresa assignments
            if not user_empresa_ids:
                current_app.logger.warning(
                    f"User {current_user.username} (ID: {current_user.id}) attempted to access "
                    f"ordenes list but has no empresa assignments"
                )
                # Return empty result for users with no empresa assignments
                result = type(
                    "obj",
                    (object,),
                    {
                        "items": [],
                        "page": 1,
                        "pages": 0,
                        "per_page": 10,
                        "total": 0,
                        "prev_num": None,
                        "next_num": None,
                        "has_prev": False,
                        "has_next": False,
                    },
                )()
                all_empresas = None
            else:
                result = services.orden_trabajo.get_ordenes_trabajo_by_user_empresas(
                    user_empresa_ids=user_empresa_ids,
                    page=page,
                    per_page=10,
                    search_codigo=search_codigo,
                    search_fecha_inicio=search_fecha_inicio,
                    search_fecha_fin=search_fecha_fin,
                )
                all_empresas = None

        return render_template(
            "list_ordenes_comentarios.html",
            username=current_user.username,
            ordenes=result["ordenes"],
            pagination=result["pagination"],
            search_filters=result["search_filters"],
            is_admin=is_admin,
            all_empresas=all_empresas,
        )

    except Exception as e:
        return _handle_route_error(e, MAIN_WELCOME_ROUTE, "list_ordenes_comentarios")


@toa_bp.route("/ordenes/<codigo>/comentarios", methods=["GET"])
@login_required
def view_orden_comentarios(codigo):
    """
    View all comentarios for a specific orden de trabajo.
    Shows comentarios with their photos if available.
    """
    try:
        # Get orden de trabajo and validate user access
        orden_trabajo = services.comentarios_use_case.get_orden_trabajo_by_codigo(
            codigo
        )

        # Check if user is admin (dev user or has admin role)
        is_admin = current_user.username == "dev" or current_user.has_roles(["admin"])

        if not orden_trabajo:
            raise ValueError(f"Orden de trabajo '{codigo}' no encontrada")

        # Admin users have access to all ordenes, regular users need validation
        if (
            not is_admin
            and not services.comentarios_use_case.validate_user_access_to_orden(
                current_user, orden_trabajo
            )
        ):
            raise ValueError(
                f"Orden de trabajo '{codigo}' no encontrada o el usuario no tiene acceso"
            )

        # Get comentarios directly from service (returns raw model objects with datetime)
        comentarios = services.comentarios.get_comentarios_by_orden_trabajo(
            orden_trabajo.id
        )

        return render_template(
            "view_orden_comentarios.html",
            username=current_user.username,
            orden_trabajo=orden_trabajo,
            comentarios=comentarios,
        )

    except ValueError as e:
        # Order not found or access denied
        flash(str(e), "error")
        return redirect(url_for("toa.list_ordenes_comentarios"))

    except Exception as e:
        return _handle_route_error(
            e, "toa.list_ordenes_comentarios", "view_orden_comentarios"
        )
