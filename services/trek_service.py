from typing import Literal

from models import Trek
from db import db

def get_all_treks():
    return Trek.query.all()

def get_trek_by_id(trek_id: int) -> Trek | None:
    return Trek.query.get(trek_id)

def create_trek(**trek_data) -> Trek | Exception:
    trek = Trek(**trek_data)
    db.session.add(trek)
    try:
        db.session.commit()
        return trek
    except Exception as e:
        db.session.rollback()
        return e

def update_trek(trek_id: int, **trek_data) -> Trek | Exception:
    trek = get_trek_by_id(trek_id)
    if not trek:
        return Exception("Trek not found")

    for key, value in trek_data.items():
        setattr(trek, key, value)

    try:
        db.session.commit()
        return trek
    except Exception as e:
        db.session.rollback()
        return e

def delete_trek_by_id(trek_id: int) -> Literal[True] | Exception:
    trek = get_trek_by_id(trek_id)
    if not trek:
        return Exception("Trek not found")

    db.session.delete(trek)
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return e