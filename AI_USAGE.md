# AI Usage

## Tools used

Codex and Gemini.

## What AI helped with

AI was used to:

- interpret the take-home requirements and implementation plan
- design the booking, payment, and trial-class data model
- identify the last-seat race condition
- outline API endpoints and state transitions
- generate initial test scenarios
- review Docker, Alembic, and README setup details
- review API validation, logging, and metrics scope

## Important design decision

The key reliability rule is that payment success does not automatically mean booking confirmation. The backend locks the trial-class row, rechecks the confirmed count against the class capacity, checks for an existing confirmed booking, and then commits the final booking status.

This ensures that two users competing for one remaining seat cannot both become confirmed.

## Where AI output was rejected or corrected

An availability check performed before the confirmation transaction would allow two concurrent requests to observe the same remaining seat. That approach was rejected in favor of PostgreSQL row-level locking with `SELECT FOR UPDATE`.

During verification, AI-generated implementation details were also corrected when the local environment exposed issues: the SQLite partial-index predicate needed a SQL expression object, stale test imports were removed, and Docker runtime dependencies were separated from development dependencies.

## Verification

The implementation was verified through:

- Python compilation checks
- unit tests for successful payment, failed payment, and capacity handling
- FastAPI integration tests for booking, payment, roster, health, metrics, and validation
- a PostgreSQL-gated concurrent last-seat test using `asyncio.gather`
- Docker Compose migration and seed startup troubleshooting
- manual API and OpenAPI endpoint checks
- `git diff --check`

## What I would improve next

With more time, I would add a real payment-provider boundary, authentication and authorization, stronger production metrics, distributed deployment checks, and a browser-level end-to-end test.
