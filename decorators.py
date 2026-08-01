from flask import flash, redirect, session, url_for
from services import UserService
from functools import wraps


def no_auth_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" in session and "user_role" in session:
            return redirect(url_for(session["user_role"].lower() + ".dashboard"))
        return view(**kwargs)
    return wrapped_view


def auth_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        user = UserService.get_active_user_by_id(session["user_id"])
        if not user:
            session.clear()
            flash("Your account is blacklisted or does not exist.", "danger")
            return redirect(url_for("auth.login"))

        return view(**kwargs)
    return wrapped_view

def roles_required(*roles: str):
    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if "user_role" not in session or session["user_role"].upper() not in roles:
                return redirect(url_for("auth.login"))
            return view(**kwargs)
        return wrapped_view
    return decorator