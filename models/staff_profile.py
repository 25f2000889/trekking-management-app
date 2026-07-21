from datetime import datetime, UTC
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db

if TYPE_CHECKING:
    from models import User


class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    experience: Mapped[str] = mapped_column(Text, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship("User", back_populates="staff_profile")

    def __init__(self, user_id: int, experience: str, phone_number: str, address: str):
        self.user_id = user_id
        self.experience = experience
        self.phone_number = phone_number
        self.address = address
        self.created_at = datetime.now(UTC)