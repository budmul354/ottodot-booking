from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Booking, BookingStatus, PaymentAttempt, PaymentStatus, Student, TrialClass
from ..observability import increment, logger


class BookingNotFoundError(Exception):
    pass


class DuplicateBookingError(Exception):
    pass


class InvalidPaymentResultError(Exception):
    pass


def create_booking(db: Session, student_id: int, trial_class_id: int) -> Booking:
    if db.get(Student, student_id) is None or db.get(TrialClass, trial_class_id) is None:
        increment("booking_validation_failed_total")
        raise BookingNotFoundError("Student or trial class not found")
    now = datetime.now(timezone.utc)
    booking = Booking(
        student_id=student_id,
        trial_class_id=trial_class_id,
        status=BookingStatus.PENDING_PAYMENT,
        created_at=now,
        updated_at=now,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    increment("booking_created_total")
    logger.info("booking_created booking_id=%s student_id=%s trial_class_id=%s", booking.id, student_id, trial_class_id)
    return booking


def record_payment(db: Session, booking_id: int, result: str) -> tuple[PaymentAttempt, Booking]:
    if result not in {"success", "failure"}:
        raise InvalidPaymentResultError("result must be 'success' or 'failure'")

    booking = db.get(Booking, booking_id)
    if booking is None:
        increment("booking_not_found_total")
        raise BookingNotFoundError("Booking not found")
    if booking.status != BookingStatus.PENDING_PAYMENT:
        increment("payment_invalid_state_total")
        raise InvalidPaymentResultError("Only pending_payment bookings accept payment")

    now = datetime.now(timezone.utc)
    payment = PaymentAttempt(
        booking_id=booking.id,
        status=PaymentStatus.SUCCEEDED if result == "success" else PaymentStatus.FAILED,
        provider_reference=f"mock-{booking.id}-{int(now.timestamp() * 1000)}",
        created_at=now,
    )
    db.add(payment)

    if result == "failure":
        booking.status = BookingStatus.PAYMENT_FAILED
        booking.updated_at = now
        db.commit()
        db.refresh(payment)
        increment("booking_payment_failed_total")
        logger.info("booking_payment_failed booking_id=%s", booking.id)
        return payment, booking

    # The class row is the serialization point for the last-seat race.
    trial_class = db.execute(
        select(TrialClass)
        .where(TrialClass.id == booking.trial_class_id)
        .with_for_update()
    ).scalar_one()
    confirmed_count = db.scalar(
        select(func.count(Booking.id)).where(
            Booking.trial_class_id == trial_class.id,
            Booking.status == BookingStatus.CONFIRMED,
        )
    ) or 0
    duplicate = db.scalar(
        select(Booking.id).where(
            Booking.student_id == booking.student_id,
            Booking.trial_class_id == booking.trial_class_id,
            Booking.status == BookingStatus.CONFIRMED,
        )
    )
    if duplicate is not None:
        db.rollback()
        increment("booking_duplicate_rejected_total")
        raise DuplicateBookingError("Student already has a confirmed booking for this class")
    if confirmed_count >= trial_class.capacity:
        booking.status = BookingStatus.CAPACITY_UNAVAILABLE
        increment("booking_capacity_rejected_total")
        logger.info("booking_capacity_rejected booking_id=%s trial_class_id=%s", booking.id, trial_class.id)
    else:
        booking.status = BookingStatus.CONFIRMED
        increment("booking_confirmation_total")
        logger.info("booking_confirmed booking_id=%s trial_class_id=%s", booking.id, trial_class.id)
    booking.updated_at = now
    db.commit()
    db.refresh(payment)
    return payment, booking
