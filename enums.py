import enum

class UserRole(enum.Enum):
    ADMIN = "Admin"
    STAFF = "Staff"
    TREKKER = "Trekker"

class UserStatus(enum.Enum):
    ACTIVE = "Active"
    PENDING = "Pending"
    REJECTED = "Rejected"
    BLACKLISTED = "Blacklisted"

class TrekDifficulty(enum.Enum):
    EASY = "Easy"
    MODERATE = "Moderate"
    HARD = "Hard"

class TrekStatus(enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    CANCELLED = "Cancelled"
    OPEN = "Open"
    COMPLETED = "Completed"

class TrekBookingStatus(enum.Enum):
    PENDING = "Pending"
    BOOKED = "Booked"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"