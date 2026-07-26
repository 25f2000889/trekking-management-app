from flask import Blueprint, session, redirect, render_template, request, url_for
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

        if not email or not password:
            return "Email and password are required", 400

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
            return "Invalid credentials", 401
    return render_template("auth/login.html")

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