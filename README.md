# Ottodot Trial Booking

## Overview

Ottodot Trial Booking is a small full-stack trial-class booking system for parents booking online science and math classes for their children. It covers the complete demo flow:

1. Select a child.
2. Select a trial class.
3. Create a pending booking.
4. Simulate payment success or failure.
5. View the final booking status.
6. View the confirmed class roster.

The central engineering concern is booking correctness under competing payments. Trial classes have a per-class capacity, failed payments never enter the roster, duplicate confirmed bookings are prevented, and concurrent attempts for the final seat are serialized with a PostgreSQL row lock.

## Architecture

- Backend: FastAPI, SQLAlchemy, PostgreSQL
- Frontend: dependency-free HTML, CSS, and JavaScript
- Migrations: Alembic
- Tests: pytest, FastAPI integration tests, PostgreSQL concurrency test
- Local orchestration: Docker Compose

The database protects the confirmed student/class uniqueness invariant. The backend owns business rules and transaction locking. The frontend displays availability for user experience only; availability is rechecked during payment confirmation.

## Run the full application with Docker

From the repository root:

```powershell
docker compose up --build
```

The Compose startup starts PostgreSQL, applies the Alembic migration, inserts the synthetic seed dataset, starts the FastAPI backend, and serves the frontend through Nginx.

Open the application at http://127.0.0.1:3000.

Useful URLs:

- Frontend: http://127.0.0.1:3000
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
- Metrics: http://127.0.0.1:8000/metrics

Stop the stack with:

```powershell
docker compose down
```

## Run locally without Docker

Create and activate the backend virtual environment:

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements-dev.txt
```

Set `DATABASE_URL` to a running PostgreSQL instance:

```powershell
$env:DATABASE_URL="postgresql+psycopg://ottodot:ottodot@localhost:5432/ottodot"
```

Apply the schema and seed data:

```powershell
alembic -c backend\alembic.ini upgrade head
python -m backend.app.seed
```

Start the backend:

```powershell
python -m uvicorn backend.app.main:app --reload
```

In a second terminal, serve the frontend:

```powershell
python -m http.server 3000 --directory frontend
```

Open http://127.0.0.1:3000.

## Run tests

Run the unit and API integration tests:

```powershell
python -m pytest backend\tests -v
```

The PostgreSQL concurrency test is skipped unless `DATABASE_URL` points to PostgreSQL. To run it with the Compose database:

```powershell
docker compose up -d db
$env:DATABASE_URL="postgresql+psycopg://ottodot:ottodot@localhost:5432/ottodot"
python -m pytest backend\tests\test_concurrency_postgres.py -v
```

The test creates two pending bookings for a class with one seat, confirms them concurrently, and verifies that exactly one booking becomes confirmed.

## API endpoints

- `GET /students`
- `GET /trial-classes`
- `POST /bookings`
- `POST /bookings/{booking_id}/payment`
- `GET /bookings/{booking_id}`
- `GET /bookings/trial-classes/{class_id}/roster`
- `GET /health`
- `GET /metrics`

## Seed scenarios

The seed data includes a class with available seats, a class with three confirmed students and one remaining seat, a full class with four confirmed students, multiple synthetic students, and a historical failed-payment booking.

## Deliberately excluded

Authentication, authorization, real payment processing, refunds, notifications, waiting lists, regular enrollment, background workers, and production UI styling are outside this time-boxed trial-booking slice.
