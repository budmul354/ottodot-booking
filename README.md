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

## Phase 3 complete

The `frontend/` directory contains a dependency-free browser UI for the full demo flow. Start the API, then serve that directory with any static server:

```powershell
python -m http.server 3000 --directory frontend
```

Open http://127.0.0.1:3000. The UI calls the backend, displays availability as informational only, records mock payment results, and refreshes the confirmed roster.

## Deliberately excluded

Authentication, authorization, real payment providers, refunds, notifications, waiting lists, regular enrollment, background workers, and production UI styling remain outside this time-boxed trial-booking slice.

## Phase 4 Sub-phase 1

Deployment and concurrency foundations are included: an Alembic initial migration, a PostgreSQL-gated concurrent last-seat test, and Docker Compose services for PostgreSQL, backend, and frontend.

## Phase 4 Sub-phase 2

The API now validates request values, returns clearer `400`, `404`, and `409` responses, and exposes `/health` and `/metrics`. Booking events are logged and counted for confirmation, payment failure, capacity rejection, duplicate rejection, and validation failures. API integration tests cover the booking/payment/roster flow and malformed input.
