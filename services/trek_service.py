from typing import Literal
from enums import TrekDifficulty
from enums import TrekStatus
from models import Trek
from sqlalchemy import or_
from db import db
from utils import escape_search_input

def get_all_treks():
    return db.session.query(Trek).all()

def search_treks(search_term: str | None = None, difficulty: TrekDifficulty | None = None, sort: str | None = None) -> list[Trek]:
    query = db.session.query(Trek).filter(Trek.status == TrekStatus.APPROVED)

    if search_term:
        search_term = escape_search_input(search_term.strip())
        query = query.filter(
            or_(
                Trek.name.ilike(f"{search_term}%", escape="\\"),
                Trek.location.ilike(f"{search_term}%", escape="\\"),
            )
        )

    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    if sort == "name_asc":
        query = query.order_by(Trek.name)
    elif sort == "name_desc":
        query = query.order_by(Trek.name.desc())
    elif sort == "date_asc":
        query = query.order_by(Trek.start_date)
    elif sort == "date_desc":
        query = query.order_by(Trek.start_date.desc())

    return query.all()

def get_assigned_treks_for_staff(staff_id: int, only_statuses: list[TrekStatus] | None = None) -> list[Trek]:
    query = db.session.query(Trek).filter(Trek.assigned_staff_id == staff_id)
    if only_statuses:
        query = query.filter(Trek.status.in_(only_statuses))
    return query.all()

def get_trek_by_id(trek_id: int, only_statuses: list[TrekStatus] | None = None) -> Trek | None:
    query = db.session.query(Trek).filter(Trek.id == trek_id)
    if only_statuses:
        query = query.filter(Trek.status.in_(only_statuses))
    return query.first()

def search_treks_by_name_or_location(search_term: str) -> list[Trek]:
    search_term = escape_search_input(search_term.strip())
    if not search_term:
        return []

    return db.session.query(Trek).filter(
        or_(
            Trek.name.ilike(f"{search_term}%", escape="\\"),
            Trek.location.ilike(f"{search_term}%", escape="\\"),
        )
    ).order_by(Trek.id).all()

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