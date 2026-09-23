# Ottodot Trial Booking

## Phase 1 complete

The repository now contains the domain and database foundation described in the implementation plan:

- SQLAlchemy models for parents, students, trial classes, bookings, and payment attempts
- PostgreSQL connection configuration through `DATABASE_URL`
- idempotent synthetic seed data covering available, last-seat, full, duplicate, and payment-failure scenarios
- separate booking and payment status enums
- positive-capacity constraint and a partial unique index for confirmed student/class bookings

See [backend/README.md](backend/README.md) for setup and seed instructions.

## Phase 2 complete

The backend now exposes the core trial booking flow:

- `GET /students`
- `GET /trial-classes`
- `POST /bookings`
- `POST /bookings/{booking_id}/payment`
- `GET /bookings/{booking_id}`
- `GET /bookings/trial-classes/{class_id}/roster`

Successful payment confirmation locks the trial-class row, rechecks capacity, checks duplicate confirmed bookings, and only then confirms the booking. A successful mock payment can therefore produce `capacity_unavailable` when another transaction wins the last seat.
