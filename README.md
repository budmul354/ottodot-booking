# Ottodot Trial Booking

## Phase 1 complete

The repository now contains the domain and database foundation described in the implementation plan:

- SQLAlchemy models for parents, students, trial classes, bookings, and payment attempts
- PostgreSQL connection configuration through `DATABASE_URL`
- idempotent synthetic seed data covering available, last-seat, full, duplicate, and payment-failure scenarios
- separate booking and payment status enums
- positive-capacity constraint and a partial unique index for confirmed student/class bookings

See [backend/README.md](backend/README.md) for setup and seed instructions.

Phase 2 will add booking/payment services, API endpoints, transaction locking, and tests.
