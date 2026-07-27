from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from decorators import auth_required
from services import UserService

shared_bp = Blueprint("shared", __name__, url_prefix="/")

@shared_bp.route("/", methods=["GET"])
def index():
    return redirect(url_for("auth.login"))


@shared_bp.route("/profile", methods=["GET", "POST"])
@auth_required
def profile():
    if request.method == "POST":
        firstName = request.form.get("first_name")
        lastName = request.form.get("last_name")

        form = {
            "first_name": firstName,
            "last_name": lastName
        }

        if not firstName:
            flash("First name is required.", "danger")
            session["form"] = form
            session["errors"] = {"first_name": "First name is required."}
            return redirect(url_for("shared.profile"))

        if not lastName:
            flash("Last name is required.", "danger")
            session["form"] = form
            session["errors"] = {"last_name": "Last name is required."}
            return redirect(url_for("shared.profile"))

        result = UserService.update_user(user_id=session['user_id'], first_name=firstName, last_name=lastName)
        
        if result is True:
            flash("Profile updated successfully", "success")
            return redirect(url_for("shared.profile"))

        flash("Database error: " + str(result), "danger")
        return redirect(url_for("shared.profile"))

    form = session.pop("form", {})
    errors = session.pop("errors", {})

    return render_template("shared/profile.html", tab="profile", _form=form, _errors=errors)