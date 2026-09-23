from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, BookingStatus, Student, TrialClass
from ..schemas import StudentRead, TrialClassRead

router = APIRouter(tags=["catalog"])


@router.get("/students", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)):
    return db.scalars(select(Student).order_by(Student.id)).all()


@router.get("/trial-classes", response_model=list[TrialClassRead])
def list_trial_classes(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            TrialClass,
            func.count(Booking.id).filter(Booking.status == BookingStatus.CONFIRMED).label("confirmed_count"),
        )
        .outerjoin(Booking, Booking.trial_class_id == TrialClass.id)
        .group_by(TrialClass.id)
        .order_by(TrialClass.starts_at)
    ).all()
    return [
        TrialClassRead(
            id=trial_class.id, title=trial_class.title, starts_at=trial_class.starts_at,
            capacity=trial_class.capacity, confirmed_count=count,
            available_seats=max(trial_class.capacity - count, 0),
        )
        for trial_class, count in rows
    ]
