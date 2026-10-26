---
stage: plan
bolt: 003-orgatex-integration
created: 2026-10-26T06:48:30Z
---

## Implementation Plan: 003-orgatex-integration

### Objective
Create the WeighingMS backend (FastAPI, port 8000) with its cross-cutting conventions, define `OrgatexPort`, implement it as the single HTTP adapter to the Dummy OrgaTEX (Brief IR-07), and expose the batch queue, batch detail and recipe to the UI in WeighingMS's own model — including the automatic scale assignment and tolerance band per component.

### 1. What will change
- New WeighingMS backend app with configuration file, standard error body, request-ID logging, and the `/api/batches…` endpoints the UI will use.
- Domain value objects/policies needed by the recipe view: exact `Quantity`, scale-selection policy, tolerance band with configurable default rule.
- `npm run dev` starts the WeighingMS API next to the dummy service.

### 2. Files to be created / modified
- `config/station.toml` — station identity, selectable statuses, scale threshold and definitions, default tolerance rule, short names (configurable without code change, NFR-13)
- `src/weighingms/config.py` — settings (env + TOML) loader
- `src/weighingms/logging_setup.py` — request-ID log format
- `src/weighingms/domain/quantity.py` — exact quantity (g/kg), conversion, display precision (g 1 dp, kg 3 dp)
- `src/weighingms/domain/scale_selection.py` — ≤ threshold → precision, else floor
- `src/weighingms/domain/tolerance.py` — tolerance band from recipe tolerance or default rule (zones follow in bolt 006)
- `src/weighingms/domain/errors.py` — `DomainError` with stable codes
- `src/weighingms/application/ports.py` — `OrgatexPort` protocol + port DTOs + integration errors
- `src/weighingms/application/batches.py` — batch query service (selectability, fabric/lot text, recipe enrichment)
- `src/weighingms/infrastructure/orgatex/contract.py` — external (Dummy OrgaTEX) contract models, kept out of the domain
- `src/weighingms/infrastructure/orgatex/http_adapter.py` — httpx adapter: list/get/recipe, status write-back, idempotent consumption posting, error translation, call logging, last-contact time
- `src/weighingms/api/app.py`, `api/errors.py`, `api/schemas.py`, `api/batches.py`, `api/middleware.py`
- `package.json` — `dev:api` added to `dev` (modified)
- Tests: `tests/unit/weighingms/test_quantity.py`, `test_scale_selection.py`, `test_tolerance_band.py`; `tests/integration/weighingms/test_orgatex_adapter.py`; `tests/api/weighingms/test_batches_api.py`; fixtures in `tests/conftest.py`

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 001-batch-queue-from-orgatex | FR-1 |
| 002-batch-detail-and-recipe-from-orgatex | FR-3, FR-4 (+ FR-8 scale assignment and FR-12 band shown in the recipe) |
| 003-consumption-write-back | FR-17 (adapter capability) |

### 4. APIs involved
Provided by WeighingMS (for the UI):
| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/batches` | `{receivedAt, batches[]}` with `fabricLot`, `selectable`, `notSelectableReason` |
| GET | `/api/batches/{batchId}` | batch header + selectability |
| GET | `/api/batches/{batchId}/recipe` | components with target, tolerance band (±, min, max, source), scale assignment, lot, short name |

Used (Dummy OrgaTEX training contract, through the adapter only): `GET /api/batches`, `GET /api/batches/{id}`, `GET /api/batches/{id}/recipe`, `PATCH /api/batches/{id}/status`, `POST /api/batches/{id}/consumption`.

Errors: 404 `BATCH_NOT_FOUND`, 503 `ORGATEX_UNAVAILABLE`, 502 `ORGATEX_BAD_DATA`.

### 5. How it will be tested
- Unit: quantity conversion/formatting, scale selection over all prototype components and the 3.000/3.001 kg boundary and a changed threshold, tolerance band from recipe and from the default rule (incl. minimums).
- Integration: the real adapter against the real dummy app in-process (Starlette `TestClient` as the httpx client) — mapping, 404, unavailable (via failure injection), status write-back, consumption idempotency.
- API: WeighingMS endpoints with the adapter wired to the dummy — queue fields and selectability, recipe enrichment (B-24187 bands and scales), 503 when OrgaTEX is down, standard error body.
- `npm run check`; manual `npm run dev` + curl through port 8000.

### Technical Approach
- Hexagonal: domain (pure) ← application (ports, services) ← infrastructure (adapters) / api. WeighingMS never imports `dummy_systems`.
- External contract types are parsed in the adapter and mapped to port DTOs; a malformed payload becomes `ORGATEX_BAD_DATA`.
- httpx with a 2 s timeout; connection errors, timeouts and 5xx → `OrgatexUnavailable`; adapter records the last successful contact time for the status strip (bolt 004).

### Acceptance Criteria
- [ ] UI-facing `GET /api/batches` returns the four batches with fabric/lot text and selectability, obtained through the adapter
- [ ] Recipe shows B-24187 components with bands 1234.0–1246.0 g, 384.0–388.0 g, 93.5–94.5 g, 23.880–24.120 kg, 9.552–9.648 kg and scales precision/precision/precision/floor/floor
- [ ] OrgaTEX down → 503 `ORGATEX_UNAVAILABLE` with a plain message; unknown batch → 404
- [ ] Status write-back and idempotent consumption posting work through the adapter
- [ ] Every OrgaTEX call is logged with method, path, status and duration
- [ ] `npm run dev` starts dummy + API; `npm run check` green

### Checkpoint — plan review (delegated, self-validated)
Implements all three stories, keeps OrgaTEX behind one adapter (IR-07), uses the agreed contracts, prepares the data the prototype's rail/header need, fully testable. **APPROVE PLAN.**
