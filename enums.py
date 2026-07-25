import enum

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    TREKKER = "TREKKER"

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    BLACKLISTED = "BLACKLISTED"

class TrekDifficulty(enum.Enum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    HARD = "HARD"

class TrekStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CANCELLED = "CANCELLED"
    OPEN = "OPEN"
    COMPLETED = "COMPLETED"

class TrekBookingStatus(enum.Enum):
    PENDING = "PENDING"
    BOOKED = "BOOKED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"