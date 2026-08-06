from sqlalchemy import or_, cast, String

from enums import UserRole, UserStatus
from models import User, StaffProfile
from db import db
from utils import escape_search_input
from werkzeug.security import generate_password_hash

from typing import Literal

def get_all_users() -> list[User]:
    return db.session.query(User).all()

def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)

def get_user_by_role(role: UserRole) -> list[User]:
    return db.session.query(User).filter_by(role=role).all()

def get_active_user_by_id(user_id: int) -> User | None:
    return db.session.query(User).filter_by(id=user_id, status=UserStatus.ACTIVE).first()

def search_users_by_id_or_name_or_email(search_term: str, role: UserRole | None = None) -> list[User]:
    search_term = escape_search_input(search_term.strip())
    if not search_term:
        return []

    query = db.session.query(User).filter(
        or_(
            cast(User.id, String).like(f"{search_term}%", escape="\\"),
            User.first_name.ilike(f"{search_term}%", escape="\\"),
            User.last_name.ilike(f"{search_term}%", escape="\\"),
            User.email.ilike(f"{search_term}%", escape="\\"),
        )
    )

    if role is not None:
        query = query.filter_by(role=role)

    return query.order_by(User.id).all()

def add_user(**user_data) -> User | Exception:
    if "email" in user_data:
        existing_user = db.session.query(User).filter_by(email=user_data["email"]).first()
        if existing_user:
            return Exception("User with this email already exists")

    if "password" in user_data:
        user_data["password_hash"] = generate_password_hash(user_data.pop("password"))
        del user_data["password"]

    user = User(**user_data)
    db.session.add(user)

    try:
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        return e

def add_staff_member(**staff_data) -> User | Exception:
    staff_member = User(
        first_name=staff_data.get("first_name", ""),
        last_name=staff_data.get("last_name", ""),
        email=staff_data.get("email", ""),
        password_hash=generate_password_hash(staff_data.get("password", "")),
        role=UserRole.STAFF,
        status=staff_data.get("status", UserStatus.PENDING)
    )
    db.session.add(staff_member)
    db.session.flush()

    staff_profile = StaffProfile(
        user_id=staff_member.id,
        experience=staff_data.get("experience", ""),
        phone_number=staff_data.get("phone_number", ""),
        address=staff_data.get("address", "")
    )
    db.session.add(staff_profile)

    try:
        db.session.commit()
        return staff_member
    except Exception as e:
        db.session.rollback()
        return e

def update_user(user_id, **user_data) -> Literal[True] | Exception:
    user = db.session.query(User).get(user_id)
    if not user:
        return Exception("User not found")

    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return e

def update_user_with_staff_profile(user_id, **user_data) -> Literal[True] | Exception:
    user = db.session.query(User).get(user_id)
    if not user:
        return Exception("User not found")

    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    staff_profile = db.session.query(StaffProfile).filter_by(user_id=user_id).first()
    if staff_profile:
        for key in ["experience", "phone_number", "address"]:
            if key in user_data:
                setattr(staff_profile, key, user_data[key])

    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return e