from typing import Literal

from models.trek import Trek
from models.trek_booking import TrekBooking
from models.user import User
from validation import ValidationError
from enum import Enum

def convert_enum_to_name_in_dict(dict: dict):
    for key, value in dict.items():
        if isinstance(value, Enum):
            dict[key] = value.name
    return dict

def convert_enum_to_name(value, enum_class):
    if value is None:
        return None
    try:
        return enum_class(value).name
    except ValueError:
        raise ValidationError(None, f"Invalid value for {enum_class.__name__}: {value}")

def escape_search_input(search_input: str) -> str:
    return search_input.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# API Responses
def trek_response(trek: Trek) -> dict:
    response = {
        "id": trek.id,
        "name": trek.name,
        "description": trek.description,
        "location": trek.location,
        "available_slots": trek.available_slots,
        "assigned_staff_id": trek.assigned_staff_id,
        "difficulty": trek.difficulty.name,
        "duration_days": trek.duration_days,
        "start_date": trek.start_date.isoformat() if trek.start_date else None,
        "end_date": trek.end_date.isoformat() if trek.end_date else None,
        "status": trek.status.name,
    }

    return response


def user_response(user: User) -> dict:
    response = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role.name,
        "status": user.status.name,
    }

    if user.staff_profile:
        response["staff_profile"] = {
            "experience": user.staff_profile.experience,
            "phone_number": user.staff_profile.phone_number,
            "address": user.staff_profile.address,
        }

    return response


def trek_booking_response(booking: TrekBooking) -> dict:
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "trek_id": booking.trek_id,
        "booking_date": booking.booking_date.isoformat() if booking.booking_date else None,
        "status": booking.status.name,
        "user": {
            "first_name": booking.user.first_name,
            "last_name": booking.user.last_name,
            "email": booking.user.email,
        },
        "trek": {
            "name": booking.trek.name,
            "location": booking.trek.location,
        },
    }