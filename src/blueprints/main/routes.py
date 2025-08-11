from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user, logout_user

from src.app.extensions import services
from src.utils.decorators import dev_only

main_bp = Blueprint("main", __name__)

# Route Constants
MAIN_MANAGE_USERS_ROUTE = "main.manage_users"


@main_bp.route("/healthcheck")
def healthcheck():
    return jsonify({"status": "ok"})


@main_bp.route("/")
def welcome():
    """Welcome page route."""
    if not current_user.is_authenticated:
        return redirect(url_for("main.login"))
    return render_template("welcome.html", username=current_user.username)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page - real user authentication."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            # Use real authentication with the User model
            from src.models.auth.user import User

            user = User.get_by_username(username)
            if user and user.verify_password(password):
                login_user(user)
                flash("¡Inicio de sesión exitoso!", "success")

                # Redirect to next page if provided, otherwise to welcome
                # Check both form data and URL args for next parameter
                next_page = request.form.get("next") or request.args.get("next")
                if next_page:
                    return redirect(next_page)
                return redirect(url_for("main.welcome"))
            else:
                flash("Usuario o contraseña incorrectos", "error")
        else:
            flash("Por favor introduce usuario y contraseña", "error")

    return render_template("login.html")


@main_bp.route("/logout")
def logout():
    """Logout route."""
    logout_user()
    flash("Has cerrado sesión", "info")
    return redirect(url_for("main.login"))


# Dev-only user management routes
@main_bp.route("/users", methods=["GET", "POST"])
@dev_only()
def manage_users():
    """
    User management panel - accessible only by 'dev' user.

    GET: Display user management form and list of users
    POST: Create a new user with supervisor role and assigned empresa
    """
    try:
        if request.method == "POST":
            # Get form data
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()
            empresa_id = request.form.get("empresa_id")

            # Convert empresa_id to int
            try:
                empresa_id = int(empresa_id) if empresa_id else None
            except ValueError:
                flash("ID de empresa inválido", "error")
                return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))

            if not all([username, password, empresa_id]):
                flash("Todos los campos son requeridos", "error")
                return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))

            # Create user through use case
            result = services.user_use_case.create_user(
                username=username, password=password, empresa_id=empresa_id
            )

            flash(result["message"], "success")
            return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))

        else:
            # GET: Show user management panel
            users_data = services.user_use_case.get_all_users_data()
            empresas_data = services.user_use_case.get_empresas_for_dropdown()

            return render_template(
                "manage_users.html",
                username=current_user.username,
                users=users_data["users"],
                empresas=empresas_data["empresas"],
            )

    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))


@main_bp.route("/users/<int:user_id>/edit", methods=["POST"])
@dev_only()
def edit_user(user_id):
    """
    Edit an existing user - accessible only by 'dev' user.
    """
    try:
        # Get form data
        username = request.form.get("username", "").strip() or None
        password = request.form.get("password", "").strip() or None
        empresa_id = request.form.get("empresa_id")

        # Convert empresa_id to int if provided
        if empresa_id:
            try:
                empresa_id = int(empresa_id)
            except ValueError:
                flash("ID de empresa inválido", "error")
                return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))

        # Update user through use case
        result = services.user_use_case.update_user(
            user_id=user_id, username=username, password=password, empresa_id=empresa_id
        )

        flash(result["message"], "success")

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))


@main_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@dev_only()
def delete_user(user_id):
    """
    Delete a user - accessible only by 'dev' user.
    """
    try:
        # Delete user through use case
        result = services.user_use_case.delete_user(user_id)
        flash(result["message"], "success")

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))


@main_bp.route("/users/<int:user_id>/restore", methods=["POST"])
@dev_only()
def restore_user(user_id):
    """
    Restore a soft-deleted user - accessible only by 'dev' user.
    """
    try:
        # Restore user through use case
        result = services.user_use_case.restore_user(user_id)
        flash(result["message"], "success")

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")

    return redirect(url_for(MAIN_MANAGE_USERS_ROUTE))
