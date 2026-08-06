from typing import Literal
from enums import TrekDifficulty, TrekStatus, TrekBookingStatus
from models import Trek
from sqlalchemy import or_
from db import db
from models import TrekBooking, User
from utils import escape_search_input

def get_all_treks():
    return db.session.query(Trek).all()

def get_trek_booking(user_id: int, trek_id: int) -> TrekBooking | None:
    return db.session.query(TrekBooking).filter(
        TrekBooking.user_id == user_id,
        TrekBooking.trek_id == trek_id
    ).first()

def get_all_trek_bookings(include_statuses: list[TrekBookingStatus] | None = None) -> list[TrekBooking]:
    query = db.session.query(TrekBooking)
    if include_statuses:
        query = query.filter(TrekBooking.status.in_(include_statuses))
    return query.all()

def get_all_trek_bookings_for_user(user_id: int, include_statuses: list[TrekBookingStatus] | None = None) -> list[TrekBooking]:
    query = db.session.query(TrekBooking).filter(TrekBooking.user_id == user_id)
    if include_statuses:
        query = query.filter(TrekBooking.status.in_(include_statuses))
    return query.all()

def get_all_trek_bookings_for_staff(staff_id: int, include_statuses: list[TrekBookingStatus] | None = None) -> list[TrekBooking]:
    query = db.session.query(TrekBooking).join(Trek).filter(Trek.assigned_staff_id == staff_id)
    if include_statuses:
        query = query.filter(TrekBooking.status.in_(include_statuses))
    return query.all()

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

def update_trek_booking(trek_booking_id: int, **trek_booking_data) -> TrekBooking | Exception:
    trek_booking = db.session.query(TrekBooking).filter(TrekBooking.id == trek_booking_id).first()
    if not trek_booking:
        return Exception("Trek booking not found")

    if trek_booking.status == TrekBookingStatus.CANCELLED and trek_booking_data.get("status") == TrekBookingStatus.BOOKED:
        trek = get_trek_by_id(trek_booking.trek_id)
        if not trek:
            return Exception("Associated trek not found")
        if trek.available_slots <= 0:
            return Exception("No available slots for this trek")
        trek.available_slots -= 1
    elif trek_booking.status == TrekBookingStatus.BOOKED and trek_booking_data.get("status") == TrekBookingStatus.CANCELLED:
        trek = get_trek_by_id(trek_booking.trek_id)
        if not trek:
            return Exception("Associated trek not found")
        trek.available_slots += 1

    for key, value in trek_booking_data.items():
        setattr(trek_booking, key, value)

    try:
        db.session.commit()
        return trek_booking
    except Exception as e:
        db.session.rollback()
        return e

def book_trek(user_id: int, trek_id: int) -> Literal[True] | Exception:
    trek = get_trek_by_id(trek_id, only_statuses=[TrekStatus.APPROVED])
    if not trek:
        return Exception("Trek not found or not available for booking")

    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        return Exception("User not found")

    already_booked = db.session.query(TrekBooking).filter(
        TrekBooking.user_id == user_id,
        TrekBooking.trek_id == trek_id
    ).first()
    if already_booked:
        return Exception("User has already booked this trek")

    if trek.available_slots <= 0:
        return Exception("No available slots for this trek")

    booking = TrekBooking(user_id=user_id, trek_id=trek_id)
    db.session.add(booking)
    trek.available_slots -= 1

    try:
        db.session.commit()
        return True
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