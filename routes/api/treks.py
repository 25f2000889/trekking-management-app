from flask import Blueprint, g, jsonify, request
from decorators import api_auth_optional, api_roles_required
from enums import TrekDifficulty, TrekStatus, UserRole
from models import Trek
from services import TrekService
from utils import trek_response
from validation import ValidationError, optional, optional_enum, optional_int, require, require_date, require_enum, require_int

api_treks_bp = Blueprint("api_treks", __name__, url_prefix="/api/treks")


def parse_trek_data(data):
    return {
        "name": require(data, "name", "Name"),
        "description": optional(data, "description"),
        "location": require(data, "location", "Location"),
        "duration_days": require_int(data, "duration_days", "Duration"),
        "difficulty": require_enum(data, "difficulty", "Difficulty", TrekDifficulty),
        "available_slots": require_int(data, "available_slots", "Available slots"),
        "start_date": require_date(data, "start_date", "Start date"),
        "end_date": require_date(data, "end_date", "End date"),
        "assigned_staff_id": optional_int(data, "assigned_staff_id", "Assigned staff"),
        "status": optional_enum(data, "status", "Status", TrekStatus) or TrekStatus.PENDING,
    }


@api_treks_bp.get("/")
@api_auth_optional
def get_treks():
    user = g.current_user

    if user and user.role == UserRole.ADMIN:
        treks = TrekService.get_all_treks()
    elif user and user.role == UserRole.STAFF:
        treks = TrekService.get_assigned_treks_for_staff(user.id)
    else:
        try:
            difficulty = optional_enum(request.args, "difficulty", "Difficulty", TrekDifficulty)
        except ValidationError as validation_error:
            return jsonify({"error": validation_error.message}), 400

        treks = TrekService.search_treks(
            search_term=request.args.get("search"),
            difficulty=difficulty,
            sort=request.args.get("sort"),
        )

    return jsonify([trek_response(trek) for trek in treks]), 200


@api_treks_bp.post("/")
@api_roles_required("ADMIN")
def create_trek():
    try:
        trek_data = parse_trek_data(request.get_json(silent=True) or {})
    except ValidationError as validation_error:
        return jsonify({"error": validation_error.message}), 400

    result = TrekService.create_trek(**trek_data)
    if not isinstance(result, Trek):
        return jsonify({"error": str(result)}), 400

    return jsonify(trek_response(result)), 201


@api_treks_bp.put("/<int:trek_id>")
@api_roles_required("ADMIN")
def update_trek(trek_id):
    if not TrekService.get_trek_by_id(trek_id):
        return jsonify({"error": "Trek not found"}), 404

    try:
        trek_data = parse_trek_data(request.get_json(silent=True) or {})
    except ValidationError as validation_error:
        return jsonify({"error": validation_error.message}), 400

    result = TrekService.update_trek(trek_id, **trek_data)
    if not isinstance(result, Trek):
        return jsonify({"error": str(result)}), 400

    return jsonify(trek_response(result)), 200


@api_treks_bp.delete("/<int:trek_id>")
@api_roles_required("ADMIN")
def delete_trek(trek_id):
    if not TrekService.get_trek_by_id(trek_id):
        return jsonify({"error": "Trek not found"}), 404

    result = TrekService.delete_trek_by_id(trek_id)
    if result is not True:
        return jsonify({"error": str(result)}), 400

    return jsonify({"message": "Trek deleted successfully"}), 200