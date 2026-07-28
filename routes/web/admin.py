from flask import Blueprint, redirect, render_template, request, url_for, session, flash

from decorators import auth_required, roles_required
from validation import ValidationError, optional, require, require_int, optional_int, require_enum, optional_enum, require_date
from utils import convert_enum_to_name_in_dict
from enums import TrekDifficulty, TrekStatus
from services import TrekService
from models import Trek

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard", methods=["GET"])
@auth_required
@roles_required("ADMIN")
def dashboard():
    # Implement logic to fetch and display admin dashboard data
    return render_template("admin/dashboard.html", tab="dashboard")


@admin_bp.route("/treks", methods=["GET"])
@auth_required
@roles_required("ADMIN")
def treks():
    treks = TrekService.get_all_treks()
    return render_template("admin/treks.html", tab="treks", treks=treks)


@admin_bp.route("/treks/add", methods=["GET", "POST"])
@auth_required
@roles_required("ADMIN")
def add_trek():
    if request.method == "POST":
        try:
            name = require(request.form, "name", "Name")
            description = optional(request.form, "description")
            location = require(request.form, "location", "Location")
            duration_days = require_int(request.form, "duration_days", "Duration")
            difficulty = require_enum(request.form, "difficulty", "Difficulty", TrekDifficulty)
            available_slots = require_int(request.form, "available_slots", "Available Slots")
            start_date = require_date(request.form, "start_date", "Start date")
            end_date = require_date(request.form, "end_date", "End date")
            assigned_staff_id = optional_int(request.form, "assigned_staff_id", "Assigned staff")
            status = optional_enum(request.form, "status", "Status", TrekStatus)
        except ValidationError as ve:
            flash(ve.message, "danger")
            session["form"] = dict(request.form)
            session["errors"] = {ve.field: ve.message}
            return redirect(url_for("admin.add_trek"))

        result = TrekService.create_trek(
            name=name,
            description=description,
            location=location,
            duration_days=duration_days,
            difficulty=difficulty,
            available_slots=available_slots,
            start_date=start_date,
            end_date=end_date,
            assigned_staff_id=assigned_staff_id if assigned_staff_id else None,
            status=status if status else TrekStatus.PENDING
        )

        if isinstance(result, Trek):
            flash("Trek created successfully", "success")
            return redirect(url_for("admin.treks"))
        else:
            flash("Database error: " + str(result), "danger")
            return redirect(url_for("admin.add_trek"))

    form = session.pop("form", {})
    errors = session.pop("errors", {})

    return render_template("admin/add_edit_trek.html", tab="treks", _form=form, _errors=errors)

@admin_bp.route("/treks/edit/<int:trek_id>", methods=["GET", "POST"])
@auth_required
@roles_required("ADMIN")
def edit_trek(trek_id: int):
    if request.method == "POST":
        try:
            name = require(request.form, "name", "Name")
            description = optional(request.form, "description")
            location = require(request.form, "location", "Location")
            duration_days = require_int(request.form, "duration_days", "Duration")
            difficulty = require_enum(request.form, "difficulty", "Difficulty", TrekDifficulty)
            available_slots = require_int(request.form, "available_slots", "Available slots")
            start_date = require_date(request.form, "start_date", "Start date")
            end_date = require_date(request.form, "end_date", "End date")
            assigned_staff_id = optional_int(request.form, "assigned_staff_id", "Assigned staff")
            status = optional_enum(request.form, "status", "Status", TrekStatus)
        except ValidationError as ve:
            flash(ve.message, "danger")
            session["form"] = dict(request.form)
            session["errors"] = {ve.field: ve.message}
            return redirect(url_for("admin.edit_trek", trek_id=trek_id))

        result = TrekService.update_trek(
            trek_id,
            name=name,
            description=description,
            location=location,
            duration_days=duration_days,
            difficulty=difficulty,
            available_slots=available_slots,
            start_date=start_date,
            end_date=end_date,
            assigned_staff_id=assigned_staff_id if assigned_staff_id else None,
            status=status if status else TrekStatus.PENDING
        )

        if isinstance(result, Trek):
            flash("Trek updated successfully", "success")
            return redirect(url_for("admin.treks"))
        else:
            flash("Database error: " + str(result), "danger")
            return redirect(url_for("admin.edit_trek", trek_id=trek_id))

    trek = TrekService.get_trek_by_id(trek_id)

    if not trek:
        flash("Trek not found", "danger")
        return redirect(url_for("admin.treks"))

    form = convert_enum_to_name_in_dict(session.pop("form", trek.__dict__))
    errors = session.pop("errors", {})
    
    return render_template("admin/add_edit_trek.html", tab="treks", trek_id=trek_id, _form=form, _errors=errors)

@admin_bp.route("/treks/delete/<int:trek_id>", methods=["POST"])
@auth_required
@roles_required("ADMIN")
def delete_trek(trek_id):
    trek = TrekService.get_trek_by_id(trek_id)

    if not trek:
        flash('Trek not found', 'danger')
        return redirect(url_for("admin.treks"))

    result = TrekService.delete_trek_by_id(trek_id)

    if result is True:
        flash('Trek deleted successfully', 'success')
    else:
        flash('Database error: ' + str(result), 'danger')

    return redirect(url_for("admin.treks"))

@admin_bp.route("/staff", methods=["GET", "POST"])
@auth_required
@roles_required("ADMIN")
def staff():
    if request.method == "POST":
        # Implement logic to create a new staff member
        pass
    # Implement logic to fetch and display staff members
    return render_template("admin/staff.html", tab="staff")


@admin_bp.route("/users", methods=["GET", "POST"])
@auth_required
@roles_required("ADMIN")
def users():
    if request.method == "POST":
        # Implement logic to create a new user
        pass
    # Implement logic to fetch and display users
    return render_template("admin/users.html", tab="users")


@admin_bp.route("/bookings", methods=["GET", "POST"])
@auth_required
@roles_required("ADMIN")
def bookings():
    if request.method == "POST":
        # Implement logic to create a new booking
        pass
    # Implement logic to fetch and display bookings
    return render_template("admin/bookings.html", tab="bookings")