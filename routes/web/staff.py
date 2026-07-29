from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from decorators import auth_required, roles_required
from services import TrekService

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")

@staff_bp.route("/dashboard", methods=["GET"])
@auth_required
@roles_required("STAFF")
def dashboard():
    return render_template("staff/dashboard.html", tab="dashboard")