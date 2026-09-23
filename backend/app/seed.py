from datetime import datetime, timedelta, timezone

from .database import SessionLocal, create_tables
from .models import Booking, BookingStatus, Parent, Student, TrialClass


def seed() -> None:
    create_tables()
    with SessionLocal.begin() as db:
        if db.query(Parent.id).first() is not None:
            print("Seed skipped: database already contains data.")
            return

        parent = Parent(name="Jordan Lee", email="jordan@example.com")
        db.add(parent)
        students = [Student(name=name, parent=parent) for name in
                    ("Alice", "Bob", "Charlie", "David", "Emily", "Frank")]
        db.add_all(students)

        now = datetime.now(timezone.utc)
        math = TrialClass(title="Math Trial", starts_at=now + timedelta(days=2), capacity=4)
        physics = TrialClass(title="Physics Trial", starts_at=now + timedelta(days=3), capacity=4)
        chemistry = TrialClass(title="Chemistry Trial", starts_at=now + timedelta(days=4), capacity=4)
        db.add_all([math, physics, chemistry])
        db.flush()

        def confirmed(student: Student, trial_class: TrialClass) -> Booking:
            return Booking(student=student, trial_class=trial_class,
                           status=BookingStatus.CONFIRMED, created_at=now, updated_at=now)

        db.add(confirmed(students[0], math))
        db.add_all([confirmed(students[i], physics) for i in range(3)])
        db.add_all([confirmed(students[i], chemistry) for i in range(4)])
        db.add(Booking(student=students[5], trial_class=math,
                       status=BookingStatus.PAYMENT_FAILED, created_at=now, updated_at=now))
    print("Seed complete.")


if __name__ == "__main__":
    seed()
