from flask import Blueprint, flash, session, redirect, render_template, request, url_for
from decorators import no_auth_required
from validation import ValidationError, require, require_enum
from utils import convert_enum_to_name_in_dict
from enums import UserRole, UserStatus
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

        try:
            email = require(request.form, "email", "Email")
            password = require(request.form, "password", "Password")
        except ValidationError as e:
            flash(str(e), "danger")
            session["form"] = form
            session["errors"] = {
                e.field: str(e)
            }
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
        try:
            first_name = require(request.form, "first_name", "First name")
            last_name = require(request.form, "last_name", "Last name")
            email = require(request.form, "email", "Email")
            password = require(request.form, "password", "Password")
            confirm_password = require(request.form, "confirm_password", "Confirm password")
            role = require_enum(request.form, "role", "Role", UserRole)
        except ValidationError as ve:
            flash(ve.message, "danger")
            session["form"] = dict(request.form)
            session["errors"] = {ve.field: ve.message}
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            session["form"] = dict(request.form)
            session["errors"] = {"confirm_password": "Passwords do not match"}
            return redirect(url_for("auth.register"))

        user_status = UserStatus.PENDING if role == UserRole.STAFF else UserStatus.ACTIVE

        user = AuthService.register(first_name, last_name, email, password, role, status=user_status)
        if isinstance(user, Exception):
            flash("Registration error: " + str(user), "danger")
            session["form"] = dict(request.form)
            return redirect(url_for("auth.register"))

        session["user_id"] = user.id
        session["user_role"] = user.role.value
        flash("Registration successful", "success")

        if user.role == UserRole.STAFF:
            return redirect(url_for("staff.dashboard"))

        return redirect(url_for("trekker.dashboard"))

    form = convert_enum_to_name_in_dict(session.pop("form", {}))
    errors = session.pop("errors", {})
    return render_template("auth/register.html", _form=form, _errors=errors)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))