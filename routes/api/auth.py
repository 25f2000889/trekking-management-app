from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from enums import UserRole
from services import AuthService
from validation import ValidationError, require, require_enum

api_auth_bp = Blueprint("api_auth", __name__, url_prefix="/api/auth")

@api_auth_bp.route("/login", methods=["POST"])
def api_login():
    data = request.get_json()

    try:
        email = require(data, "email", "Email")
        password = require(data, "password", "Password")
    except ValidationError as ve:
        return jsonify({"error": ve.message}), 400

    user = AuthService.login(email, password)
    if user:
        token = create_access_token(identity=str(user.id), additional_claims={"role": user.role.name, "status": user.status.name})
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "user_role": user.role.name,
            "access_token": token
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@api_auth_bp.route("/register", methods=["POST"])
def api_register():
    data = request.get_json()

    try:
        email = require(data, "email", "Email")
        password = require(data, "password", "Password")
        first_name = require(data, "first_name", "First name")
        last_name = require(data, "last_name", "Last name")
    except ValidationError as ve:
        return jsonify({"error": ve.message}), 400

    user = AuthService.register(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role=UserRole.TREKKER
    )
    if isinstance(user, Exception):
        return jsonify({"error": str(user)}), 400
    
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role.name, "status": user.status.name})
    return jsonify({
        "message": "Registration successful",
        "user_id": user.id,
        "user_role": user.role.name,
        "access_token": token
    }), 201