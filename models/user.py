from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db

if TYPE_CHECKING:
    from models import Trek, TrekBooking, StaffProfile


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)

    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="TREKKER",
    )  # ADMIN, STAFF, TREKKER

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )  # ACTIVE, PENDING, BLACKLISTED

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    assigned_treks: Mapped[list["Trek"]] = relationship(
        back_populates="assigned_staff",
        lazy="select",
    )

    trek_bookings: Mapped[list["TrekBooking"]] = relationship(
        back_populates="user",
        lazy="select",
    )

    staff_profile: Mapped["StaffProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
    )

    def __init__(self, first_name: str, last_name: str, email: str, password_hash: str, role: str = "TREKKER", status: str = "ACTIVE"):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.status = status
        self.created_at = datetime.now(UTC)