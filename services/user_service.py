from models import User
from db import db

from typing import Literal

def update_user(user_id, first_name=None, last_name=None) -> Literal[True] | Exception:
    user = User.query.get(user_id)
    if not user:
        return Exception("User not found")

    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name

    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return e