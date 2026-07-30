from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from decorators import auth_required, roles_required

trekker_bp = Blueprint("trekker", __name__, url_prefix="/trekker")

@trekker_bp.route("/dashboard", methods=["GET"])
@auth_required
@roles_required("TREKKER")
def dashboard():
    return render_template("trekker/dashboard.html", tab="dashboard")
