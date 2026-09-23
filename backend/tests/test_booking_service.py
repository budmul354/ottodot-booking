from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models import Booking, BookingStatus, Parent, Student, TrialClass
from backend.app.services.booking_service import (
    create_booking,
    record_payment,
)


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        now = datetime.now(timezone.utc)
        parent = Parent(name="Test Parent", email="test@example.com")
        student = Student(name="Alice", parent=parent)
        trial_class = TrialClass(title="Test Trial", starts_at=now, capacity=1)
        session.add_all([parent, student, trial_class])
        session.commit()
        yield session, student, trial_class


def test_successful_payment_confirms_booking(db):
    session, student, trial_class = db
    booking = create_booking(session, student.id, trial_class.id)
    payment, updated = record_payment(session, booking.id, "success")
    assert payment.status.value == "succeeded"
    assert updated.status == BookingStatus.CONFIRMED


def test_failed_payment_does_not_enter_roster(db):
    session, student, trial_class = db
    booking = create_booking(session, student.id, trial_class.id)
    _, updated = record_payment(session, booking.id, "failure")
    assert updated.status == BookingStatus.PAYMENT_FAILED
    assert session.scalar(select(func.count(Booking.id)).where(Booking.status == BookingStatus.CONFIRMED)) == 0


def test_last_seat_is_not_overbooked(db):
    session, student, trial_class = db
    second = Student(name="Bob", parent=student.parent)
    session.add(second)
    session.commit()
    first = create_booking(session, student.id, trial_class.id)
    second_booking = create_booking(session, second.id, trial_class.id)
    record_payment(session, first.id, "success")
    _, updated = record_payment(session, second_booking.id, "success")
    assert updated.status == BookingStatus.CAPACITY_UNAVAILABLE
    assert session.scalar(select(func.count(Booking.id)).where(Booking.status == BookingStatus.CONFIRMED)) == 1
