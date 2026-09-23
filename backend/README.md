# Backend foundation

This package is the Phase 1 domain and database foundation for the Ottodot trial booking flow.

## Local setup

1. Create a PostgreSQL database named `ottodot` and set `DATABASE_URL` (see `.env.example`).
2. Install `requirements.txt`.
3. From the repository root, run `python -m backend.app.seed`.

`create_tables()` is intentionally a small bootstrap for the time-boxed exercise. For deployed environments, use `alembic upgrade head`.

From the repository root, `docker compose up --build` starts PostgreSQL, runs the migration and seed, then starts the API and frontend.

## Invariants represented in the schema

- Trial class capacity must be positive and is stored per class; the application will enforce the capacity during confirmation.
- A partial unique index allows multiple non-confirmed attempts but only one confirmed booking per student and trial class.
- Booking and payment statuses are separate because a successful payment can still lose the last available seat.
