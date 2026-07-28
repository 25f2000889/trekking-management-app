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