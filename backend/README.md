# Backend foundation

This package contains the backend for the Ottodot trial-booking flow. It owns booking, payment, capacity, and roster invariants; the frontend is only a presentation layer.

## Local setup

1. Create a PostgreSQL database named `ottodot` and set `DATABASE_URL` (see `.env.example`).
2. Install `requirements.txt`.
3. From the repository root, run `python -m backend.app.seed`.

`create_tables()` is intentionally a small bootstrap for the time-boxed exercise. For deployed environments, use `alembic upgrade head`.

From the repository root, `docker compose up --build` starts PostgreSQL, runs the migration and seed, then starts the API and frontend.

## Data model

- `parents`: synthetic parent records.
- `students`: children belonging to a parent.
- `trial_classes`: class title, start time, and positive capacity.
- `bookings`: student/class relationship, status, timestamps, and the confirmed-booking uniqueness constraint.
- `payment_attempts`: payment result and provider reference for each booking attempt.

The database schema is defined in `alembic/versions/0001_initial_schema.py`. Capacity is counted from confirmed bookings only. A partial unique index on `(student_id, trial_class_id)` where the booking is `confirmed` prevents duplicate confirmed bookings while allowing pending or failed attempts to remain auditable.

## API and backend actions

- `GET /students` and `GET /trial-classes` provide the booking catalog and availability display.
- `POST /bookings` creates a `pending_payment` booking.
- `POST /bookings/{booking_id}/payment` records a mock success or failure and performs final confirmation checks.
- `GET /bookings/{booking_id}` returns booking state.
- `GET /bookings/trial-classes/{class_id}/roster` returns confirmed students only.
- `GET /health` and `GET /metrics` expose operational checks.

The main domain functions are `create_booking()` and `record_payment()` in `app/services/booking_service.py`.

## Booking and payment statuses

Bookings use `pending_payment`, `confirmed`, `payment_failed`, and `capacity_unavailable`. Payment attempts use `pending`, `succeeded`, or `failed`. A successful payment can therefore still produce `capacity_unavailable` if another payment took the final seat first.

## Duplicate bookings and payment failure

The service checks for an existing confirmed booking for the same student and class before confirmation, and the database partial unique index is the final protection against duplicates. A failed payment creates a failed payment attempt and changes the booking to `payment_failed`; it is never included in the confirmed roster and does not consume capacity.

## Last-seat race

At payment confirmation, `record_payment()` locks the relevant `trial_classes` row with `SELECT ... FOR UPDATE`, counts confirmed bookings while holding that lock, checks for a duplicate confirmed booking, and then confirms or marks the booking `capacity_unavailable`. Two users can create pending bookings, but their confirmation transactions serialize on the class row, so at most one can confirm the last seat.

The tradeoff is a simple, reliable per-class serialization point: concurrent payments for the same class wait briefly, while unrelated classes can proceed independently. Availability shown in the UI is advisory and can become stale; the backend always rechecks it during payment confirmation.

## Responsibility boundaries

- UI: show availability and statuses, guide the parent through the mock payment, and display the roster. UI availability is not authoritative.
- Backend: validate requests, create bookings, process payment results, enforce capacity and duplicate rules, and expose the roster.
- Database: persist state, enforce foreign keys and confirmed-booking uniqueness, and provide the row lock used for last-seat serialization.
- Background job: not required for this synchronous mock flow. A production version would use one for payment-provider reconciliation, expiry of abandoned pending bookings, notifications, and metrics aggregation.

## Invariants represented in the schema

- Trial class capacity must be positive and is stored per class; the application will enforce the capacity during confirmation.
- A partial unique index allows multiple non-confirmed attempts but only one confirmed booking per student and trial class.
- Booking and payment statuses are separate because a successful payment can still lose the last available seat.

## Verification

`tests/test_booking_service.py` covers successful payment, payment failure, and capacity handling. `tests/test_api.py` covers the HTTP flow, roster output, validation, health, and metrics. `tests/test_concurrency_postgres.py` runs the last-seat race against PostgreSQL and verifies that exactly one concurrent payment confirms.
