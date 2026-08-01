from datetime import datetime, UTC
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums import TrekBookingStatus
from db import db

if TYPE_CHECKING:
    from models import User, Trek


class TrekBooking(db.Model):
    __tablename__ = 'trek_bookings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    trek_id: Mapped[int] = mapped_column(ForeignKey("treks.id"), nullable=False)
    booking_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    status: Mapped[TrekBookingStatus] = mapped_column(
        Enum(TrekBookingStatus),
        nullable=False,
        default=TrekBookingStatus.BOOKED,
    )

    user: Mapped["User"] = relationship("User", back_populates="trek_bookings")
    trek: Mapped["Trek"] = relationship("Trek", back_populates="trek_bookings")

    def __init__(self, user_id: int, trek_id: int, status: TrekBookingStatus = TrekBookingStatus.BOOKED):
        self.user_id = user_id
        self.trek_id = trek_id
        self.status = status
        self.booking_date = datetime.now(UTC)