from flask import Blueprint, redirect, render_template, request, url_for

from decorators import auth_required, roles_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard", methods=["GET"])
@auth_required
@roles_required("ADMIN")
def dashboard():
    # Implement logic to fetch and display admin dashboard data
    return render_template("admin/dashboard.html")