from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    parent: Mapped["Parent"] = relationship(back_populates="students")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="student")
