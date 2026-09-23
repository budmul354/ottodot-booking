from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, BookingStatus, PaymentStatus, Student
from ..schemas import (
    BookingCreate, BookingCreated, BookingRead, PaymentCreate, PaymentResult,
    RosterRead, RosterStudent,
)
from ..services.booking_service import (
    BookingNotFoundError, DuplicateBookingError, InvalidPaymentResultError,
    create_booking, record_payment,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingCreated, status_code=status.HTTP_201_CREATED)
def post_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    try:
        booking = create_booking(db, payload.student_id, payload.trial_class_id)
    except BookingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"booking_id": booking.id, "status": booking.status.value}


@router.post("/{booking_id}/payment", response_model=PaymentResult)
def post_payment(booking_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    try:
        payment, booking = record_payment(db, booking_id, payload.result)
    except BookingNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (DuplicateBookingError, InvalidPaymentResultError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"payment_status": payment.status.value, "booking_status": booking.status.value}


@router.get("/trial-classes/{class_id}/roster", response_model=RosterRead)
def get_roster(class_id: int, db: Session = Depends(get_db)):
    students = db.scalars(
        select(Student)
        .join(Booking, Booking.student_id == Student.id)
        .where(Booking.trial_class_id == class_id, Booking.status == BookingStatus.CONFIRMED)
        .order_by(Student.id)
    ).all()
    return {"class_id": class_id, "students": [RosterStudent(student_id=s.id, name=s.name) for s in students]}


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking
