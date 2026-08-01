from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from decorators import auth_required, roles_required
from enums import TrekDifficulty, TrekStatus, TrekBookingStatus
from validation import optional, optional_enum
from services import TrekService

trekker_bp = Blueprint("trekker", __name__, url_prefix="/trekker")

@trekker_bp.get("/dashboard")
@auth_required
@roles_required("TREKKER")
def dashboard():
    return render_template("trekker/dashboard.html", tab="dashboard")

@trekker_bp.get("/treks")
@auth_required
@roles_required("TREKKER")
def treks():
    search_term = optional(request.args, "search")
    difficulty = optional_enum(request.args, "difficulty", "Difficulty", enum_class=TrekDifficulty)
    sort = optional(request.args, "sort")

    treks = TrekService.search_treks(search_term=search_term, difficulty=difficulty, sort=sort)

    trek_bookings = TrekService.get_all_trek_bookings_for_user(user_id=int(session.get("user_id", "0")), include_statuses=[TrekBookingStatus.BOOKED])

    already_booked_treks = [booking.trek_id for booking in trek_bookings]

    form = request.args
    return render_template("trekker/treks.html", tab="treks", treks=treks, already_booked_treks=already_booked_treks, _form=form)

@trekker_bp.get("/treks/<int:trek_id>")
@auth_required
@roles_required("TREKKER")
def trek_details(trek_id):
    trek = TrekService.get_trek_by_id(trek_id)
    if not trek:
        flash("Trek not found.", "danger")
        return redirect(url_for("trekker.treks"))

    trek_booking = TrekService.get_trek_booking(user_id=int(session.get("user_id", "0")), trek_id=trek_id)

    return render_template("trekker/trek_details.html", tab="treks", trek=trek, trek_booking=trek_booking)

@trekker_bp.post("/treks/<int:trek_id>/book")
@auth_required
@roles_required("TREKKER")
def book_trek(trek_id):
    trek = TrekService.get_trek_by_id(trek_id, only_statuses=[TrekStatus.APPROVED])
    if not trek:
        flash("Trek not found.", "danger")
        return redirect(url_for("trekker.treks"))

    if trek.available_slots <= 0:
        flash("No available slots for this trek.", "danger")
        return redirect(url_for("trekker.trek_details", trek_id=trek_id))

    user_id = int(session.get("user_id", "0"))
    success = TrekService.book_trek(user_id=user_id, trek_id=trek_id)

    if success is True:
        flash("Successfully booked the trek!", "success")
    else:
        flash("Failed to book trek: " + str(success), "danger")

    return redirect(url_for("trekker.trek_details", trek_id=trek_id))
