from flask import Blueprint, redirect, render_template, request, url_for, session, flash

from decorators import auth_required, roles_required
from validation import ValidationError, optional, require, require_int, optional_int, require_enum, optional_enum, require_date
from utils import convert_enum_to_name_in_dict
from enums import TrekDifficulty, TrekStatus, UserRole, UserStatus
from services import TrekService, UserService
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
    search_term = request.args.get("search", "")
    if search_term:
        search_term = search_term.strip()
        treks = TrekService.search_treks_by_name_or_location(search_term)
    else:
        treks = TrekService.get_all_treks()
        
    return render_template("admin/treks.html", tab="treks", treks=treks, _form={"search": request.args.get("search", "")})


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

    staff_list = UserService.get_user_by_role(UserRole.STAFF)

    return render_template("admin/add_edit_trek.html", tab="treks", _form=form, _errors=errors, staff_list=staff_list)

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

    staff_list = UserService.get_user_by_role(UserRole.STAFF)
    
    return render_template("admin/add_edit_trek.html", tab="treks", trek_id=trek_id, _form=form, _errors=errors, staff_list=staff_list)

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

@admin_bp.route("/staff", methods=["GET"])
@auth_required
@roles_required("ADMIN")
def staff():
    search_term = request.args.get("search", "")
    if search_term:
        search_term = search_term.strip()
        staff = UserService.search_users_by_id_or_name_or_email(search_term, role=UserRole.STAFF)
    else:
        staff = UserService.get_user_by_role(UserRole.STAFF)

    pending = [s for s in staff if s.status == UserStatus.PENDING]
    active = [s for s in staff if s.status == UserStatus.ACTIVE]
    blacklisted = [s for s in staff if s.status == UserStatus.BLACKLISTED]

    return render_template("admin/staff.html", tab="staff", staff={
        "pending": pending,
        "active": active,
        "blacklisted": blacklisted,
    }, _form={"search": request.args.get("search", "")})

@admin_bp.route("/staff/approve/<int:staff_member_id>", methods=["POST"])
@auth_required
@roles_required("ADMIN")
def approve_staff(staff_member_id):
    result = UserService.update_user(staff_member_id, status=UserStatus.ACTIVE)

    if result is True:
        flash('Staff member approved successfully', 'success')
    else:
        flash('Error: ' + str(result), 'danger')

    return redirect(url_for("admin.staff"))

@admin_bp.route("/staff/reject/<int:staff_member_id>", methods=["POST"])
@auth_required
@roles_required("ADMIN")
def reject_staff(staff_member_id):
    result = UserService.update_user(staff_member_id, status=UserStatus.REJECTED)

    if result is True:
        flash('Staff member rejected successfully', 'success')
    else:
        flash('Error: ' + str(result), 'danger')

    return redirect(url_for("admin.staff"))

@admin_bp.route("/staff/blacklist/<int:staff_member_id>", methods=["POST"])
@auth_required
@roles_required("ADMIN")
def blacklist_staff(staff_member_id):
    result = UserService.update_user(staff_member_id, status=UserStatus.BLACKLISTED)

    if result is True:
        flash('Staff member blacklisted successfully', 'success')
    else:
        flash('Error: ' + str(result), 'danger')

    return redirect(url_for("admin.staff"))


@admin_bp.route("/trekkers", methods=["GET"])
@auth_required
@roles_required("ADMIN")
def trekkers():
    search_term = request.args.get("search", "")
    if search_term:
        search_term = search_term.strip()
        trekkers = UserService.search_users_by_id_or_name_or_email(search_term, role=UserRole.TREKKER)
    else:
        trekkers = UserService.get_user_by_role(UserRole.TREKKER)
    
    active = [s for s in trekkers if s.status == UserStatus.ACTIVE]
    blacklisted = [s for s in trekkers if s.status == UserStatus.BLACKLISTED]
    
    return render_template("admin/users.html", tab="trekkers", _form={"search": request.args.get("search", "")}, trekkers={
        "active": active,
        "blacklisted": blacklisted,
    })

@admin_bp.route("/trekkers/blacklist/<int:trekker_id>", methods=["POST"])
@auth_required
@roles_required("ADMIN")
def blacklist_trekker(trekker_id):
    result = UserService.update_user(trekker_id, status=UserStatus.BLACKLISTED)

    if result is True:
        flash('Trekker blacklisted successfully', 'success')
    else:
        flash('Error: ' + str(result), 'danger')

    return redirect(url_for("admin.trekkers"))

@admin_bp.route("/trekkers/activate/<int:trekker_id>", methods=["POST"])
@auth_required
@roles_required("ADMIN")
def activate_trekker(trekker_id):
    result = UserService.update_user(trekker_id, status=UserStatus.ACTIVE)

    if result is True:
        flash('Trekker activated successfully', 'success')
    else:
        flash('Error: ' + str(result), 'danger')

    return redirect(url_for("admin.trekkers"))


@admin_bp.route("/bookings", methods=["GET", "POST"])
@auth_required
@roles_required("ADMIN")
def bookings():
    if request.method == "POST":
        # Implement logic to create a new booking
        pass
    # Implement logic to fetch and display bookings
    return render_template("admin/bookings.html", tab="bookings")