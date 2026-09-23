from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class BookingStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PAYMENT_FAILED = "payment_failed"
    CANCELLED = "cancelled"
    CAPACITY_UNAVAILABLE = "capacity_unavailable"


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index(
            "uq_confirmed_student_trial_class",
            "student_id",
            "trial_class_id",
            unique=True,
            postgresql_where="status = 'confirmed'",
            sqlite_where="status = 'confirmed'",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    trial_class_id: Mapped[int] = mapped_column(
        ForeignKey("trial_classes.id"), nullable=False
    )
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, native_enum=False, length=32),
        nullable=False,
        default=BookingStatus.PENDING_PAYMENT,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    student: Mapped["Student"] = relationship(back_populates="bookings")
    trial_class: Mapped["TrialClass"] = relationship(back_populates="bookings")
    payment_attempts: Mapped[list["PaymentAttempt"]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )
