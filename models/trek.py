from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enums import TrekDifficulty, TrekStatus
from db import db

if TYPE_CHECKING:
    from models import User, TrekBooking


class Trek(db.Model):
    __tablename__ = "treks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)

    difficulty: Mapped[TrekDifficulty] = mapped_column(
        Enum(TrekDifficulty),
        nullable=False,
    )

    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)

    available_slots: Mapped[int] = mapped_column(Integer, nullable=False)

    assigned_staff_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    status: Mapped[TrekStatus] = mapped_column(
        Enum(TrekStatus),
        nullable=False,
        default=TrekStatus.PENDING,
    )

    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)

    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    assigned_staff: Mapped["User | None"] = relationship(back_populates="assigned_treks")

    trek_bookings: Mapped[list["TrekBooking"]] = relationship(
        back_populates="trek",
        lazy="select",
    )

    def __init__(
        self,
        name: str,
        location: str,
        difficulty: TrekDifficulty,
        duration_days: int,
        available_slots: int,
        start_date: date,
        end_date: date,
        description: str | None = None,
        assigned_staff_id: int | None = None,
        status: TrekStatus = TrekStatus.PENDING,
    ):
        self.name = name
        self.location = location
        self.difficulty = difficulty
        self.duration_days = duration_days
        self.available_slots = available_slots
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.assigned_staff_id = assigned_staff_id
        self.status = status
        self.created_at = datetime.now(UTC)