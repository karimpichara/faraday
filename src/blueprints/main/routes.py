from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/healthcheck")
def healthcheck():
    return jsonify({"status": "ok"})


@main_bp.route("/")
def welcome():
    """Welcome page route."""
    if "username" not in session:
        return redirect(url_for("main.login"))
    return render_template("welcome.html", username=session["username"])


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page - real user authentication."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            # Use real authentication with the User model
            from src.models.auth.user import User

            if User.authenticate(username, password):
                session["username"] = username
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
    session.pop("username", None)
    flash("Has cerrado sesión", "info")
    return redirect(url_for("main.login"))
