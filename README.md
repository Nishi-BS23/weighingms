# WeighingMS

An assisted dyestuff weighing station, as a training build made with the specs.md **AI-DLC** flow.

WeighingMS takes an operator through an OrgaTEX batch recipe one component at a time:
- It picks the scale automatically: the 3 kg precision scale up to 3 kg, the 32 kg floor scale above that.
- It shows the live weight against a configurable tolerance band, and allows Confirm only while the weight is within tolerance.
- It records every weighing (lot, container, tare, scale, operator).
- It writes actual consumption back to OrgaTEX and prints a weighing ticket.

> **Training build.** OrgaTEX, the two scales, the barcode scanner and the ticket printer are replaced by **Dummy
> APIs** (`src/dummy_systems`, port 8100). Their contracts are training contracts only. They make no claim about
> the real OrgaTEX interface or real device protocols, which are still open questions for FCI (UQ-01 … UQ-14 in
> `memory-bank/intents/001-assisted-dyestuff-weighing/requirements.md`).

## Quick start

```bash
python3.13 -m venv .venv      # project-local virtualenv; Poetry reuses it
npm run setup                 # npm packages (root, frontend, playwright), Chromium, Python packages
npm run dev                   # starts all three processes
```

Then open **http://127.0.0.1:5173**.

| Process | URL | What it is |
|---|---|---|
| `web` | http://127.0.0.1:5173 | Operator terminal (React + Vite); `/api` is proxied to the station API |
| `api` | http://127.0.0.1:8000 (`/docs`) | WeighingMS station API (FastAPI) |
| `dummy` | http://127.0.0.1:8100 (`/docs`) | Training substitutes for OrgaTEX, scales, scanner and printer |

**Prerequisites:**
- Python 3.13 (developed with 3.13.5).
- Poetry 2.x.
- Node.js `^20.19` or `>=22.13` (developed with 22.22).

If another virtualenv is active in your shell, run Poetry as `VIRTUAL_ENV= poetry install`.

## Using the station

1. **Select batch.** Touch a row, or type or scan a batch ID such as `B-24187` (the keyboard-wedge scanner) and
   press Enter.
2. **Weigh.**
   - The active component shows its lot, container and tare.
   - The scale is selected automatically.
   - *Weighed now*, *Still to weigh* and *Target* update live, with a tolerance bar and a status line.
   - **OK · Confirm (F1)** is enabled only within tolerance.
   - **Re-tare (F2)** zeroes the scale. **Quit (F4)** leaves safely and keeps the confirmed components.
   - **Supervisor override** accepts an out-of-tolerance weight with a supervisor PIN and a reason.
3. **Confirm & print.**
   - Shows the summary, the per-component results and the OrgaTEX write-back status (with **Retry** when it is
     PENDING).
   - **Print ticket (F1)**; reprints are marked REPRINT. **Next batch (F3)**.

**Training controls** (training mode only):
- **Above the terminal**, as in the prototype: **Simulate dispense** pours to just inside tolerance;
  **Simulate overshoot** pours past it; **Reset** resets the weighing.
- **Below the terminal:** each external system can be switched offline, and **Reset training data** restores the
  seed.

The training supervisor PIN is **2468**: S. Ahmed, SV-2001.

## Tests

```bash
npm run check       # backend: ruff format + lint, mypy --strict, pytest with coverage (≥ 80 %)
                    # frontend: prettier, eslint (type-checked), tsc, vitest
npm run test:e2e    # Playwright (Chromium): B-24187 end to end + failure scenarios; reuses `npm run dev`
```

| Suite | Count | Where |
|---|---|---|
| Backend unit, integration and API | 214 tests, 97.9 % coverage | `tests/unit`, `tests/integration`, `tests/api` |
| Frontend components and hooks | 50 tests | `frontend/src/**/*.test.ts(x)` |
| End-to-end | 11 tests: workflow, boundaries, 9 failure scenarios | `playwright/tests` |

The Playwright HTML report and videos are written to `playwright/playwright-report` and
`playwright/test-results`. Open the report with `npm --prefix playwright run report`.

## Architecture

```
Browser (React)  ──/api──▶  WeighingMS API (FastAPI)  ──HTTP──▶  Dummy APIs (FastAPI)
  frontend/                   src/weighingms/                       src/dummy_systems/
                              domain → application → infrastructure    orgatex · scale · scanner
                              (pure rules)  (services/ports)  (adapters,   · printer · control
                                                               SQLite)
```

- **The domain is free of I/O.**
  - Quantities are exact `Decimal`s, sent over the API as decimal strings with a unit.
  - Tolerance bands are inclusive.
  - The tolerance zones are UNDER, NEAR, WITHIN, OVER and OFFLINE.
- **The backend decides.** `canConfirm`, the status text and the allowed actions come from the API. Confirm
  re-reads the scale on the server.
- **Mocks are kept separate.** Every external system is reached through a port and an HTTP adapter, so a real
  OrgaTEX client or scale driver replaces the adapter only.
- **Persistence.** SQLite (WAL, `synchronous=FULL`) under `data/`, with Alembic migrations. Confirmed records are
  immutable. Write-back is idempotent, keyed on the session ID.
- **Decisions.** ADR-001 to ADR-004 are in `memory-bank/standards/decision-index.md`: live-weight polling,
  recipe snapshot, training endpoints, and overshoot handled by blocking and recovering.

## Configuration

`config/station.toml` holds everything below; changing it needs no code change.

| Setting | Value in this build |
|---|---|
| Station | STN-01, "STATION 01", EN, Asia/Dhaka |
| Training mode | `training_mode = true` (mounts `/api/training/*` and shows the training panel) |
| Scale-selection threshold | 3 kg |
| Scale definitions | `scale-3kg`, `scale-32kg` |
| Default tolerance | 0.5 % of target, with a per-scale minimum; used when the recipe gives none |
| Ticket | header and short names |
| Containers | containers and their tares |
| Operators | operators, including the supervisor's PIN hash |

Seed data is in `data/seed/orgatex-seed.json`. B-24187 is taken exactly from the prototype; the other batches are
labelled invented training data.

## WeighingMS API (port 8000)

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/batches` · `/api/batches/{id}` · `/api/batches/{id}/recipe` | Batch queue, detail and recipe from OrgaTEX |
| POST | `/api/sessions` | Start or resume weighing a batch |
| GET | `/api/sessions/{id}` | Session state (components, progress, active component) |
| POST | `/api/sessions/{id}/components/{cid}/activate` | Make a pending component active (selects its scale and tares it) |
| GET | `/api/sessions/{id}/live` | Live weight already evaluated: zone, remaining, surplus, `canConfirm`, status text |
| POST | `/api/sessions/{id}/retare` · `/confirm` · `/override` · `/quit` | Weighing actions |
| POST | `/api/sessions/{id}/complete` · `/sync` | Complete the batch (409 if incomplete); retry a PENDING write-back |
| GET | `/api/sessions/{id}/summary` · `/api/weighing-records?batchId=` | Completed-batch summary and records |
| GET / POST | `/api/sessions/{id}/ticket` · `/ticket/print` | Ticket preview; print or reprint |
| GET | `/api/devices/status` · `/api/scanner/scans` | Status strip; scanner events |
| GET / POST | `/api/operators/current` · `/api/operators/sign-in` | Operator identification |
| * | `/api/training/*` | Training controls (training mode only) |

Errors use the same shape everywhere: `{"error": {"code", "message", "details"}}`, with plain-language messages.

## Dummy APIs (port 8100, training contracts)

| System | Endpoints |
|---|---|
| OrgaTEX | `GET /api/batches[?status=]`, `GET /api/batches/{id}`, `GET /api/batches/{id}/recipe`, `POST`/`GET /api/batches/{id}/consumption` (idempotent by `idempotencyKey`), `PATCH /api/batches/{id}/status` |
| Scales | `GET /api/scales`, `GET /api/scales/{id}/status`, `GET /api/scales/{id}/weight`, `POST /api/scales/{id}/tare` |
| Scanner | `POST`/`GET /api/scanner/scans`, `GET /api/scanner/status` |
| Printer | `POST`/`GET /api/tickets`, `GET /api/tickets/{id}`, `GET /api/printer/status` |
| Control | `GET /api/control/availability`, `PUT /api/control/availability/{system}`, `POST /api/control/scales/{id}/simulate`, `POST /api/control/scales/{id}/load`, `PUT /api/control/scales/{id}/calibration`, `POST /api/control/reset` |

## Repository layout

| Path | Contents |
|---|---|
| `docs/` | Brief, UI/UX prototype, project requirement |
| `memory-bank/` | AI-DLC artifacts: standards, intent (requirements, system context, units, stories), bolts, maintenance log |
| `src/weighingms/`, `src/dummy_systems/` | Station backend; training substitutes |
| `frontend/` | Operator terminal (React 19, TypeScript, Vite) |
| `tests/` | pytest suites |
| `playwright/` | End-to-end suites |
| `config/`, `data/seed/` | Station configuration; seed data |
| `evidence/` | Workbook step evidence |
| `FINAL-EVIDENCE.md` | Requirement → UI / API / code / test / evidence matrix |
