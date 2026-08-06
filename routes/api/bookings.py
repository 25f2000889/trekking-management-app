from flask import Blueprint, g, jsonify, request
from decorators import api_auth_required, api_roles_required
from enums import TrekBookingStatus, UserRole
from models import TrekBooking
from services import TrekService
from utils import trek_booking_response
from validation import ValidationError, require_int

api_bookings_bp = Blueprint("api_bookings", __name__, url_prefix="/api/bookings")


@api_bookings_bp.get("/")
@api_auth_required
def get_bookings():
	user = g.current_user

	if user.role == UserRole.ADMIN:
		bookings = TrekService.get_all_trek_bookings()
	elif user.role == UserRole.STAFF:
		bookings = TrekService.get_all_trek_bookings_for_staff(user.id)
	else:
		bookings = TrekService.get_all_trek_bookings_for_user(user.id)

	return jsonify([trek_booking_response(booking) for booking in bookings]), 200


@api_bookings_bp.post("/")
@api_roles_required("TREKKER")
def book_trek():
	try:
		trek_id = require_int(request.get_json(silent=True) or {}, "trek_id", "Trek ID")
	except ValidationError as validation_error:
		return jsonify({"error": validation_error.message}), 400

	result = TrekService.book_trek(g.current_user.id, trek_id)
	if result is not True:
		return jsonify({"error": str(result)}), 400

	booking = TrekService.get_trek_booking(g.current_user.id, trek_id)

	if not booking:
		return jsonify({"error": "Booking not found after creation"}), 404
    
	return jsonify(trek_booking_response(booking)), 201


def update_booking_status(booking_id, status, action):
	result = TrekService.update_trek_booking(booking_id, status=status)
	if not isinstance(result, TrekBooking):
		error_status = 404 if str(result) == "Trek booking not found" else 400
		return jsonify({"error": str(result)}), error_status

	return jsonify({"message": f"Booking {action} successfully", "booking": trek_booking_response(result)}), 200


@api_bookings_bp.post("/<int:booking_id>/cancel")
@api_roles_required("ADMIN")
def cancel_booking(booking_id):
	return update_booking_status(booking_id, TrekBookingStatus.CANCELLED, "cancelled")


@api_bookings_bp.post("/<int:booking_id>/restore")
@api_roles_required("ADMIN")
def restore_booking(booking_id):
	return update_booking_status(booking_id, TrekBookingStatus.BOOKED, "restored")