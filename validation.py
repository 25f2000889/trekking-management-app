from datetime import date
from enum import Enum

class ValidationError(Exception):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(message)


def optional(form, field):
    value = form.get(field)

    if not value:
        return None

    return value

def require(form, field, label):
    value = optional(form, field)

    if not value:
        raise ValidationError(field, f"{label} is required")

    return value

def optional_int(form, field, label) -> int | None:
    value = optional(form, field)

    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        raise ValidationError(field, f"{label} must be a valid integer")

def require_int(form, field, label) -> int:
    value = optional_int(form, field, label)

    if value is None:
        raise ValidationError(field, f"{label} must be a valid integer")
    return value

def optional_enum[E: Enum](form, field, label, enum_class: type[E]) -> E | None:
    value = optional(form, field)

    if not value:
        return None

    try:
        return enum_class[value]
    except KeyError:
        raise ValidationError(field, f"{label} must be a valid {enum_class.__name__}")

def require_enum[E: Enum](form, field, label, enum_class: type[E]) -> E:
    value = optional_enum(form, field, label, enum_class)

    if value is None:
        raise ValidationError(field, f"{label} must be a valid {enum_class.__name__}")
    return value

def optional_date(form, field, label) -> date | None:
    value = optional(form, field)

    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValidationError(field, f"{label} must be a valid date")

def require_date(form, field, label) -> date:
    value = optional_date(form, field, label)

    if value is None:
        raise ValidationError(field, f"{label} must be a valid date")
    return value