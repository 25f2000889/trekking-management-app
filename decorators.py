from flask import flash, redirect, session, url_for, g
from flask_jwt_extended import jwt_required, get_jwt_identity
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


# API decorators
def api_auth_required(view):
    @wraps(view)
    @jwt_required()
    def wrapped_view(**kwargs):
        user_id = get_jwt_identity()
        user = UserService.get_active_user_by_id(user_id)
        if not user:
            return {"error": "User not found or blacklisted"}, 401
        g.current_user = user
        return view(**kwargs)
    return wrapped_view

def api_auth_optional(view):
    @wraps(view)
    @jwt_required(optional=True)
    def wrapped_view(**kwargs):
        user_id = get_jwt_identity()
        if user_id is None:
            g.current_user = None
            return view(**kwargs)
        
        user = UserService.get_active_user_by_id(user_id)
        if not user:
            return {"error": "User not found or blacklisted"}, 401
        g.current_user = user
        return view(**kwargs)
    return wrapped_view

def api_roles_required(*roles: str):
    def decorator(view):
        @wraps(view)
        @api_auth_required
        def wrapped_view(*args, **kwargs):
            user = g.current_user
            if user.role.name not in roles:
                return {"error": "You do not have permission to access this resource"}, 403
            return view(*args, **kwargs)
        return wrapped_view
    return decorator