from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from decorators import auth_required, roles_required
from enums import TrekDifficulty
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

    form = request.args
    return render_template("trekker/treks.html", tab="treks", treks=treks, _form=form)
