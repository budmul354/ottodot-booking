import asyncio
import os
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models import Booking, BookingStatus, Parent, Student, TrialClass
from backend.app.services.booking_service import create_booking, record_payment


def test_concurrent_last_seat_allows_only_one_confirmation():
    async def run():
        return await _run_concurrent_test()
    asyncio.run(run())


async def _run_concurrent_test():
    url = os.getenv("DATABASE_URL", "")
    if not url.startswith("postgresql"):
        pytest.skip("Set DATABASE_URL to PostgreSQL to run the concurrency test")
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    token = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    with Session.begin() as db:
        parent = Parent(name=f"Race Parent {token}", email=f"race-{token}@example.com")
        a = Student(name="Race A", parent=parent)
        b = Student(name="Race B", parent=parent)
        trial = TrialClass(title=f"Race Trial {token}", starts_at=datetime.now(timezone.utc), capacity=1)
        db.add_all([parent, a, b, trial])
    with Session() as db:
        parent = db.scalar(select(Parent).where(Parent.email == f"race-{token}@example.com"))
        students = db.scalars(select(Student).where(Student.parent_id == parent.id).order_by(Student.id)).all()
        trial = db.scalar(select(TrialClass).where(TrialClass.title == f"Race Trial {token}"))
        ids = [create_booking(db, student.id, trial.id).id for student in students]

    def confirm(booking_id):
        with Session() as db:
            return record_payment(db, booking_id, "success")[1].status

    results = await asyncio.gather(*(asyncio.to_thread(confirm, booking_id) for booking_id in ids))
    with Session() as db:
        count = db.scalar(select(func.count(Booking.id)).where(Booking.trial_class_id == trial.id, Booking.status == BookingStatus.CONFIRMED))
    assert count == 1
    assert sum(result == BookingStatus.CONFIRMED for result in results) == 1
