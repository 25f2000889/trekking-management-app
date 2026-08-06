from flask import Blueprint, g, jsonify, request
from decorators import api_auth_required, api_roles_required
from enums import UserRole, UserStatus
from services import UserService
from utils import user_response
from validation import ValidationError, require

api_users_bp = Blueprint("api_users", __name__, url_prefix="/api/users")

STAFF_PROFILE_FIELDS = {"experience", "phone_number", "address"}
USER_PROFILE_FIELDS = {"first_name", "last_name"}

def parse_user_update(data, user):
	if not isinstance(data, dict):
		raise ValidationError(None, "Request body must be a JSON object")

	unexpected_fields = set(data) - USER_PROFILE_FIELDS - STAFF_PROFILE_FIELDS
	if unexpected_fields:
		raise ValidationError(None, f"Unsupported fields: {', '.join(sorted(unexpected_fields))}")

	if not data:
		raise ValidationError(None, "At least one profile field is required")

	staff_profile_data = STAFF_PROFILE_FIELDS.intersection(data)
	if staff_profile_data and user.role != UserRole.STAFF:
		raise ValidationError(None, "Staff profile fields can only be updated by staff members")
	if staff_profile_data and not user.staff_profile:
		raise ValidationError(None, "Staff profile not found")

	return {
		field: require(data, field, field.replace("_", " ").title())
		for field in data
	}


def update_user_status(user_id, status, action):
	user = UserService.get_user_by_id(user_id)
	if not user:
		return jsonify({"error": "User not found"}), 404
	if user.role == UserRole.ADMIN:
		return jsonify({"error": "Admin accounts cannot be modified through this endpoint"}), 400

	result = UserService.update_user(user_id, status=status)
	if result is not True:
		return jsonify({"error": str(result)}), 400

	return jsonify({"message": f"User {action} successfully", "user": user_response(user)}), 200


@api_users_bp.get("/")
@api_roles_required("ADMIN")
def get_users():
	users = UserService.get_all_users()
	return jsonify([user_response(user) for user in users]), 200


@api_users_bp.put("/<int:user_id>")
@api_auth_required
def update_user(user_id):
	if g.current_user.id != user_id:
		return jsonify({"error": "You can only update your own profile"}), 403

	try:
		user_data = parse_user_update(request.get_json(silent=True), g.current_user)
	except ValidationError as validation_error:
		return jsonify({"error": validation_error.message}), 400

	if g.current_user.role == UserRole.STAFF and STAFF_PROFILE_FIELDS.intersection(user_data):
		result = UserService.update_user_with_staff_profile(user_id, **user_data)
	else:
		result = UserService.update_user(user_id, **user_data)

	if result is not True:
		return jsonify({"error": str(result)}), 400

	return jsonify(user_response(g.current_user)), 200


@api_users_bp.post("/staff/<int:user_id>/approve")
@api_roles_required("ADMIN")
def approve_staff(user_id):
	user = UserService.get_user_by_id(user_id)
	if not user:
		return jsonify({"error": "User not found"}), 404
	if user.role != UserRole.STAFF or user.status != UserStatus.PENDING:
		return jsonify({"error": "Only pending staff requests can be approved"}), 400

	return update_user_status(user_id, UserStatus.ACTIVE, "approved")


@api_users_bp.post("/staff/<int:user_id>/reject")
@api_roles_required("ADMIN")
def reject_staff(user_id):
	user = UserService.get_user_by_id(user_id)
	if not user:
		return jsonify({"error": "User not found"}), 404
	if user.role != UserRole.STAFF or user.status != UserStatus.PENDING:
		return jsonify({"error": "Only pending staff requests can be rejected"}), 400

	return update_user_status(user_id, UserStatus.REJECTED, "rejected")


@api_users_bp.post("/<int:user_id>/blacklist")
@api_roles_required("ADMIN")
def blacklist_user(user_id):
	return update_user_status(user_id, UserStatus.BLACKLISTED, "blacklisted")


@api_users_bp.post("/<int:user_id>/restore")
@api_roles_required("ADMIN")
def restore_user(user_id):
	return update_user_status(user_id, UserStatus.ACTIVE, "restored")