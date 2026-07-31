from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from decorators import auth_required, roles_required
from enums import TrekBookingStatus, TrekStatus
from services import TrekService
from validation import ValidationError, require_int

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")

@staff_bp.get("/dashboard")
@auth_required
@roles_required("STAFF")
def dashboard():
    return render_template("staff/dashboard.html", tab="dashboard")

@staff_bp.get("/treks")
@auth_required
@roles_required("STAFF")
def treks():
    treks = TrekService.get_assigned_treks_for_staff(session['user_id'], only_statuses=[TrekStatus.APPROVED, TrekStatus.STARTED, TrekStatus.COMPLETED])

    active_bookings = {}

    for trek in treks:
        active_bookings[trek.id] = len(list(filter(lambda booking: booking.status == TrekBookingStatus.BOOKED, trek.trek_bookings)))

    return render_template("staff/treks.html", tab="treks", treks=treks, active_bookings=active_bookings)

@staff_bp.route("/treks/<int:trek_id>", methods=["GET", "POST"])
@auth_required
@roles_required("STAFF")
def trek_details(trek_id: int):
    trek = TrekService.get_trek_by_id(trek_id, only_statuses=[TrekStatus.APPROVED, TrekStatus.STARTED, TrekStatus.COMPLETED])

    if not trek or trek.assigned_staff_id != session['user_id']:
        flash("Trek not found or you are not assigned to this trek", "danger")
        return redirect(url_for("staff.treks"))

    if request.method == "POST":
        form = request.form

        try:
            available_slots = require_int(form, "available_slots", "Available Slots")

            if available_slots < 0:
                raise ValidationError("available_slots", "Available Slots cannot be negative")
        except ValidationError as e:
            flash(e.message, "danger")
            session["form"] = form
            session["errors"] = {e.field: e.message}
            return redirect(url_for("staff.trek_details", trek_id=trek_id))

        result = TrekService.update_trek(trek_id, available_slots=available_slots)

        if isinstance(result, Exception):
            flash("Database error: " + str(result), "danger")
            return redirect(url_for("staff.trek_details", trek_id=trek_id))

        flash("Available slots updated successfully", "success")
        return redirect(url_for("staff.trek_details", trek_id=trek_id))

    active_bookings = list(filter(lambda booking: booking.status == TrekBookingStatus.BOOKED, trek.trek_bookings))

    form = session.pop("form", {})
    errors = session.pop("errors", {})

    return render_template("staff/trek_details.html", tab="treks", trek=trek, active_bookings=active_bookings, _form=form, _errors=errors)

@staff_bp.post("/treks/<int:trek_id>/start")
@auth_required
@roles_required("STAFF")
def start_trek(trek_id: int):
    trek = TrekService.get_trek_by_id(trek_id, only_statuses=[TrekStatus.APPROVED, TrekStatus.STARTED, TrekStatus.COMPLETED])
    
    if not trek or trek.assigned_staff_id != session['user_id']:
        flash("Trek not found or you are not assigned to this trek", "danger")
        return redirect(url_for("staff.treks"))

    result = TrekService.update_trek(trek_id, status=TrekStatus.STARTED)

    if isinstance(result, Exception):
        flash("Database error: " + str(result), "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek_id))

    flash("Trek marked as started successfully", "success")
    return redirect(url_for("staff.trek_details", trek_id=trek_id))

@staff_bp.post("/treks/<int:trek_id>/cancel")
@auth_required
@roles_required("STAFF")
def cancel_trek(trek_id: int):
    trek = TrekService.get_trek_by_id(trek_id, only_statuses=[TrekStatus.APPROVED, TrekStatus.STARTED, TrekStatus.COMPLETED])
    
    if not trek or trek.assigned_staff_id != session['user_id']:
        flash("Trek not found or you are not assigned to this trek", "danger")
        return redirect(url_for("staff.treks"))

    result = TrekService.update_trek(trek_id, status=TrekStatus.CANCELLED)

    if isinstance(result, Exception):
        flash("Database error: " + str(result), "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek_id))

    flash("Trek marked as cancelled successfully", "success")
    return redirect(url_for("staff.treks"))

@staff_bp.post("/treks/<int:trek_id>/complete")
@auth_required
@roles_required("STAFF")
def complete_trek(trek_id: int):
    trek = TrekService.get_trek_by_id(trek_id, only_statuses=[TrekStatus.APPROVED, TrekStatus.STARTED, TrekStatus.COMPLETED])
    
    if not trek or trek.assigned_staff_id != session['user_id']:
        flash("Trek not found or you are not assigned to this trek", "danger")
        return redirect(url_for("staff.treks"))

    result = TrekService.update_trek(trek_id, status=TrekStatus.COMPLETED)

    if isinstance(result, Exception):
        flash("Database error: " + str(result), "danger")
        return redirect(url_for("staff.trek_details", trek_id=trek_id))

    flash("Trek marked as completed successfully", "success")
    return redirect(url_for("staff.trek_details", trek_id=trek_id))