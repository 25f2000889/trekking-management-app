from datetime import datetime, UTC
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db

if TYPE_CHECKING:
    from models import User, Trek


class TrekBooking(db.Model):
    __tablename__ = 'trek_bookings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trek_id: Mapped[int] = mapped_column(ForeignKey("treks.id"), nullable=False)
    booking_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='PENDING')  # BOOKED, CANCELLED, COMPLETED

    user: Mapped["User"] = relationship("User", back_populates="trek_bookings")
    trek: Mapped["Trek"] = relationship("Trek", back_populates="trek_bookings")

    def __init__(self, user_id: int, trek_id: int, status: str = 'PENDING'):
        self.user_id = user_id
        self.trek_id = trek_id
        self.status = status
        self.booking_date = datetime.now(UTC)