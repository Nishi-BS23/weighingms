---
stage: implement
bolt: 001-training-substitutes
created: 2026-10-26T06:40:19Z
---

## Implementation Walkthrough: 001-training-substitutes

### Summary

The repository now has its backend tooling and a separate training-substitutes service whose first part is the Dummy OrgaTEX. It serves the batch queue, batch detail and recipes from a seed file reproducing the prototype, and stores batch status write-backs and idempotent consumption postings in its own SQLite file. `npm run dev` starts it on port 8100.

### Structure Overview

The dummy service is a FastAPI app built by a factory, so tests can give it an isolated database and a fixed clock. Shared conventions (camelCase models, decimal-string quantities, standard error body, durable SQLite engine, injectable clock) live in `common`; everything OrgaTEX-specific lives in `orgatex` (models, seed loader, store, router). Immutable reference data comes from the seed file; mutable state goes to SQLite.

### Completed Work

- [x] `pyproject.toml` - Poetry project, dependencies, ruff/mypy/pytest/coverage configuration
- [x] `poetry.toml` - project-local `.venv`
- [x] `package.json` - root scripts `dev`, `dev:dummy`, `check`, `check:py`; `concurrently`
- [x] `.gitignore` - virtualenv, caches, node modules, SQLite runtime files, Playwright output
- [x] `README.md` - setup, run, check, Dummy OrgaTEX training contract
- [x] `data/seed/orgatex-seed.json` - B-24187 exactly as the prototype; B-24188, B-24190, B-24191 labelled invented training data
- [x] `src/dummy_systems/app.py` - app factory, default paths, health endpoint, training-contract description
- [x] `src/dummy_systems/common/models.py` - camelCase base model and exact `Quantity`
- [x] `src/dummy_systems/common/errors.py` - standard error body and handlers (API errors, validation, unknown routes)
- [x] `src/dummy_systems/common/db.py` - SQLite engine with WAL and synchronous=FULL
- [x] `src/dummy_systems/common/clock.py` - injectable UTC clock
- [x] `src/dummy_systems/orgatex/models.py` - training contract models (batch, recipe, consumption, status)
- [x] `src/dummy_systems/orgatex/seed.py` - seed loading with consistency checks (recipe ownership, component count, sequence)
- [x] `src/dummy_systems/orgatex/store.py` - status overrides and consumption postings with idempotency
- [x] `src/dummy_systems/orgatex/routes.py` - the six Dummy OrgaTEX endpoints
- [x] `src/weighingms/__init__.py` - placeholder package for the WeighingMS backend (filled from bolt 003)

### Key Decisions

- **App factory with `--factory`**: no database is created at import time; tests and dev runs choose their own paths.
- **`.venv/bin/python` in npm scripts**: the user's shell activates another project's virtualenv; calling the project interpreter directly makes `npm run dev` immune to that.
- **Router dependencies parameter**: lets bolt 002 add availability (failure injection) without changing the OrgaTEX routes.
- **Idempotency by unique key**: a repeated posting returns the original receipt with `duplicate: true`; a concurrent duplicate is caught by the unique constraint.

### Deviations from Plan

None.

### Dependencies Added

- [x] `fastapi`, `uvicorn[standard]`, `pydantic`, `sqlalchemy`, `alembic`, `httpx` - approved stack
- [x] `pytest`, `pytest-cov`, `ruff`, `mypy` - approved tooling
- [x] `concurrently` (npm) - run several dev processes from `npm run dev`

### Developer Notes

`ruff format`, `ruff check` and `mypy --strict` pass. A smoke run of `npm run dev` served `/api/batches` and returned the standard 404 body for an unknown batch.

### Stage checkpoint (delegated, self-validated)

All plan deliverables exist, standards are followed, lint and types pass. **Approved** — proceed to Test.
