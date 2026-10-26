# Data Stack

## Overview
WeighingMS persists its own traceability data in a local SQLite database accessed through SQLAlchemy 2.0, with schema changes managed by Alembic. The training Dummy OrgaTEX keeps its data in a separate store, so WeighingMS reaches OrgaTEX data only through the API, as it would in production.

## Database
**SQLite**, configured with WAL journal mode and `synchronous=FULL`.

Two separate stores:
- **`weighingms.db` (WeighingMS):** weighing sessions, weighing records, overrides, compensations, audit events, sync queue, and WeighingMS-owned master data (operators, containers, scales). Cached OrgaTEX data, if any, is never authoritative (DR-03).
- **Dummy OrgaTEX store (training substitute):** seeded from a JSON file (batch B-24187 and the other training batches, recipes, components, dyestuffs); consumption postings persisted in its own SQLite file. WeighingMS must not read or write these tables directly.

Rationale:
- The data is relational (Product Brief §9) and the volume is a single station, so a file-based database is sufficient (A-11).
- No database server to install for training participants; the driver ships with Python.
- WAL + `synchronous=FULL` make a committed transaction durable, so a confirmed weighing survives immediate power loss (NFR-05).
- Keeping the Dummy OrgaTEX in its own store preserves constraint C-01 (OrgaTEX is the source of truth; WeighingMS is not a second one) and makes the consumption write-back (FR-26, IR-05) a real, separate record that can be shown as evidence.

Self-hosted, local file. No managed service.

## ORM / Database Client
**SQLAlchemy 2.0** (typed ORM, `Mapped[...]` declarations) with **Alembic** for migrations.

Rationale:
- Standard, mature, fully typed Python data access that fits FastAPI.
- Keeps persistence models separate from Pydantic API models, matching DDD Construction Bolts where the domain model is designed first and mapped to storage afterwards.
- Alembic versions the schema, so changes made in later Bolts are explicit and reviewable.

Considered and not chosen: SQLModel (merges API and persistence models, which DDD keeps apart; less mature) and raw `sqlite3` (more hand-written code).

## Decision Relationships
- **Exact quantities (NFR-16) ↔ SQLite:** SQLite has no exact decimal type, and SQLAlchemy `Numeric` on SQLite round-trips through floating point. Therefore every quantity column (target, actual, tare, tolerance min/max, surplus, compensation targets) uses a custom SQLAlchemy column type that stores a `Decimal` as text. All arithmetic is done in Python `Decimal` in the domain layer; SQL is never used to add, subtract or compare quantities.
- **Immutability (DR-02) ↔ data access:** confirmed weighing records, overrides and audit events are insert-only. Corrections are new records referencing the original; no update or delete paths are provided for them.
- **Tech stack:** Python 3.13 + FastAPI (see `tech-stack.md`). Database access happens only in the backend; the React UI never touches storage directly.
- **Dummy OrgaTEX boundary ↔ IR-07:** all OrgaTEX interaction goes through a single adapter calling the (dummy) OrgaTEX API. Swapping the dummy for a real interface must not change WeighingMS's database.
