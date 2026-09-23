from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class TrialClass(Base):
    __tablename__ = "trial_classes"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_trial_classes_capacity_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=4)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="trial_class")
