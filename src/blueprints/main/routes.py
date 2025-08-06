from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session, url_for)

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
    """Login page - accepts any username/password."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            # Fake authentication - any credentials work
            session["username"] = username
            flash("¡Inicio de sesión exitoso!", "success")
            return redirect(url_for("main.welcome"))
        else:
            flash("Por favor introduce usuario y contraseña", "error")

    return render_template("login.html")


@main_bp.route("/logout")
def logout():
    """Logout route."""
    session.pop("username", None)
    flash("Has cerrado sesión", "info")
    return redirect(url_for("main.login"))
