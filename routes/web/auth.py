from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from decorators import no_auth_required
from enums import UserRole
from services import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
@no_auth_required
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        form = {
            "email": email
        }

        if not email:
            flash("Email is required", "danger")
            session["form"] = form
            session["errors"] = {"email": "Email is required"}
            return redirect(url_for("auth.login"))

        if not password:
            flash("Password is required", "danger")
            session["form"] = form
            session["errors"] = {"password": "Password is required"}
            return redirect(url_for("auth.login"))

        user = AuthService.login(email, password)
        if user:
            session["user_id"] = user.id
            session["user_role"] = user.role.value
            if user.role == UserRole.ADMIN:
                return redirect(url_for("admin.dashboard"))
            elif user.role == UserRole.STAFF:
                return redirect(url_for("staff.dashboard"))

            return redirect(url_for("trekker.dashboard"))
        else:
            flash("Invalid email or password", "danger")
            session["form"] = form
            return redirect(url_for("auth.login"))

    form = session.pop("form", {})
    errors = session.pop("errors", {})
    return render_template("auth/login.html", _form=form, _errors=errors)

@auth_bp.route("/register", methods=["GET", "POST"])
@no_auth_required
def register():
    if request.method == "POST":
        # Implement registration logic here
        pass
    return render_template("auth/register.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))