---
stage: plan
bolt: 001-training-substitutes
created: 2026-10-26T06:37:00Z
---

## Implementation Plan: 001-training-substitutes

### Objective
Create the repository's backend skeleton and the **Dummy OrgaTEX** training service: a separate FastAPI app (port 8100) serving the workbook's training contract from the prototype seed data, storing status changes and idempotent consumption postings. Root `npm run dev` starts it.

### 1. What will change
- The repository gains its build tooling (Poetry project with a project-local `.venv` on pyenv Python 3.13.5; root `package.json`; ruff/mypy/pytest configuration; `.gitignore`).
- A new Python package `dummy_systems` with the Dummy OrgaTEX routes, models, seed loader and store.
- A seed file with the prototype training scenario.
- `npm run dev` starts the dummy service; `npm run check` runs format check, lint, type check and tests.

### 2. Files to be created
- `pyproject.toml`, `poetry.toml` (in-project venv), `poetry.lock`
- `package.json`, `package-lock.json` (devDependency `concurrently`)
- `.gitignore`, `README.md` (setup + run instructions; Dummy contract marked "training contract")
- `src/dummy_systems/__init__.py`
- `src/dummy_systems/app.py` — app factory, router registration, standard error handler
- `src/dummy_systems/common/errors.py` — `{"error": {code, message, details}}` responses
- `src/dummy_systems/common/models.py` — camelCase base model, `Quantity` (decimal string + unit)
- `src/dummy_systems/orgatex/models.py` — Batch, BatchList, Recipe, RecipeComponent, ConsumptionPosting, ConsumptionReceipt, StatusUpdate
- `src/dummy_systems/orgatex/seed.py` — loads and validates `data/seed/orgatex-seed.json`
- `src/dummy_systems/orgatex/store.py` — SQLAlchemy store (batch status overrides, consumption postings) in `data/dummy.db`
- `src/dummy_systems/orgatex/routes.py` — the six endpoints
- `data/seed/orgatex-seed.json` — B-24187 (prototype values) + B-24188, B-24190, B-24191 (labelled invented training data, TA-19)
- `tests/api/dummy_systems/test_orgatex_api.py`, `tests/conftest.py`

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 001-dummy-orgatex-batch-queue | FR-25, FR-1 (data source) |
| 002-dummy-orgatex-recipe | FR-25, FR-3, FR-4, FR-5 (data source) |
| 003-dummy-orgatex-consumption-and-status | FR-25, FR-17 (receiver) |

### 4. APIs involved (Dummy OrgaTEX — training contract, not the real OrgaTEX interface)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/batches?status=` | Batch queue (`{generatedAt, batches[]}`) |
| GET | `/api/batches/{batchId}` | Batch header |
| GET | `/api/batches/{batchId}/recipe` | Recipe with components |
| POST | `/api/batches/{batchId}/consumption` | Store consumption once per `idempotencyKey` |
| GET | `/api/batches/{batchId}/consumption` | Stored postings (evidence) |
| PATCH | `/api/batches/{batchId}/status` | Status write-back (QUEUED/WEIGHING/WEIGHED/CANCELLED) |

Quantities are JSON strings with a unit (`{"value": "94.0", "unit": "g"}`), never JSON numbers (coding standards, NFR-11).

### 5. How it will be tested
- pytest + FastAPI `TestClient` with a temporary SQLite file per test:
  - list, status filter, detail, 404 `BATCH_NOT_FOUND`
  - B-24187 recipe values exactly equal to the prototype (targets, tolerances, lots, sequence)
  - quantities serialised as strings
  - seed integrity (every batch has a recipe; `componentCount` = number of components)
  - consumption post → 200; same key again → `duplicate: true`, one stored posting; zero lines → 422; unknown batch → 404
  - status PATCH visible in the queue; invalid status → 422
- `npm run check` (ruff format --check, ruff check, mypy --strict, pytest with coverage ≥ 80%)
- Manual curl of the three GET endpoints (Workbook STEP-18 evidence)

### Dependencies
- Python 3.13.5 (pyenv) — approved tech stack
- Poetry, npm (installed) — approved package managers
- Runtime: fastapi, uvicorn[standard], pydantic, sqlalchemy, alembic, httpx
- Dev: pytest, pytest-cov, ruff, mypy; npm `concurrently`

### Technical Approach
- App factory `create_app(db_path, seed_path)` so tests get isolated stores; module-level `app` for Uvicorn.
- Seed is immutable reference data loaded at startup; mutable state (status overrides, postings) lives in SQLite so it survives restarts until reset (reset arrives in bolt 002).
- Idempotency via a unique constraint on `idempotency_key`; duplicates return the original receipt.
- `npm run dev` uses `.venv/bin/python -m uvicorn` directly so an unrelated activated virtualenv in the user's shell cannot hijack it.

### Acceptance Criteria
- [ ] `curl :8100/api/batches` lists B-24187, B-24188, B-24190, B-24191 with all fields
- [ ] `curl :8100/api/batches/B-24187` returns SO-9931, JET-04, 100% CTN knit, 480 kg, Teal 4C, 5, QUEUED
- [ ] `curl :8100/api/batches/B-24187/recipe` returns the 5 prototype components with exact values
- [ ] Unknown batch → 404 with the standard error body
- [ ] Consumption posting idempotent and retrievable; status PATCH works
- [ ] `npm run dev` starts the dummy service; `npm run check` green

### Checkpoint 5 — plan review (delegated, self-validated)
| Question | Answer |
|----------|--------|
| Does this plan implement the stories? | Yes — each AC of stories 001–003 maps to an endpoint and a test above |
| Does it respect the architecture? | Yes — separate dummy service, own store, no WeighingMS imports (system-context) |
| Does it use the agreed APIs? | Yes — workbook training contract (`/api/batches…`) plus status/consumption evidence endpoints from FR-25 |
| Does it preserve the UI/UX? | N/A for this bolt (data only); seed matches the prototype exactly |
| Can I test it? | Yes — pytest API tests + curl evidence |

**APPROVE PLAN** — proceed to Implement.
