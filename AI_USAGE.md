# AI Usage

## Tools used

Codex and Gemini.

## What I used AI for

- Discussing the application structure and data model
- Enumerating payment and last-seat race-condition tests
- Reviewing API and frontend scope

## Where AI helped

AI helped identify that capacity must be rechecked after payment, inside a transaction that locks the trial-class row.

## Where I rejected an approach

I rejected checking availability only before payment confirmation because two users could both observe the final seat. Confirmation now locks the class row and rechecks capacity.

## Verification

The implementation was statically compiled and checked with `git diff --check`. Runtime tests require installing the dependencies listed in `backend/requirements.txt`.
