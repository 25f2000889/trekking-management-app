from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from decorators import auth_required
from validation import ValidationError, optional, require
from services import UserService

shared_bp = Blueprint("shared", __name__, url_prefix="/")

@shared_bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("auth.login"))


@shared_bp.route("/profile", methods=["GET", "POST"])
@auth_required
def profile():
    if request.method == "POST":
        form = request.form
        try:
            firstName = require(form, "first_name", "First Name")
            lastName = require(form, "last_name", "Last Name")
        except ValidationError as e:
            session["form"] = form
            session["errors"] = {e.field: e.message}
            return redirect(url_for("shared.profile"))

        user_data = {
            "first_name": firstName,
            "last_name": lastName,
        }
        password = optional(form, "password")
        if password:
            user_data["password"] = password

        if session.get('user_role', '').lower() == 'staff':
            try:
                experience = require(form, "experience", "Experience")
                phoneNumber = require(form, "phone_number", "Phone Number")
                address = require(form, "address", "Address")
            except ValidationError as e:
                session["form"] = form
                session["errors"] = {e.field: e.message}
                return redirect(url_for("shared.profile"))

            result = UserService.update_user_with_staff_profile(
                user_id=session['user_id'],
                experience=experience,
                phone_number=phoneNumber,
                address=address,
                **user_data,
            )
        else:
            result = UserService.update_user(user_id=session['user_id'], **user_data)
        
        if result is True:
            flash("Profile updated successfully", "success")
            return redirect(url_for("shared.profile"))

        flash("Database error: " + str(result), "danger")
        session["form"] = form
        return redirect(url_for("shared.profile"))

    form = session.pop("form", {})
    errors = session.pop("errors", {})

    return render_template("shared/profile.html", tab="profile", _form=form, _errors=errors)