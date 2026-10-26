# Coding Standards

## Overview
Automated formatting and strict linting/type checking for both the Python backend and the React/TypeScript frontend, a domain-driven backend layout, and a test strategy in which the Dummy APIs act as the deterministic test doubles for every external system. All checks run from one command at each Bolt's Test stage.

## Code Formatting

**Python — Tool**: Ruff formatter (Black-compatible)
**Key Settings**:
- Line length: 100
- Quotes: double

**TypeScript — Tool**: Prettier (defaults)
**Key Settings**:
- Line length: 100
- Indentation: 2 spaces
- Semicolons, double quotes, trailing commas (Prettier defaults)

**Enforcement**: format on save in the editor; verified by the project `check` command at every Bolt's Test stage. No git hooks.

## Linting

**Python — Tool**: Ruff (rule sets: pyflakes `F`, pycodestyle `E`/`W`, isort `I`, bugbear `B`, pyupgrade `UP`, simplify `SIM`) + mypy
**Strictness**: strict

**TypeScript — Tool**: ESLint with `typescript-eslint` (recommended type-checked) + `eslint-plugin-react-hooks`
**Base Config**: `tsconfig` with `strict: true`
**Strictness**: strict

**Key Rules**:
- mypy `--strict`: on - type hints are required on all Python code so agents and reviewers can rely on them
- TypeScript `any`: not allowed - use `unknown` and narrow
- `print` / `console.log` in committed code: not allowed - use the logger
- Commented-out code: not allowed - git keeps history
- Floating point for quantities: not allowed - NFR-16; quantities are `Decimal` in Python and decimal strings over the API

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Python modules | snake_case | `tolerance_rule.py` |
| Python functions / variables | snake_case | `evaluate_tolerance`, `target_qty` |
| Python classes | PascalCase | `WeighingRecord`, `ToleranceBand` |
| Python constants | UPPER_SNAKE | `PRECISION_SCALE_MAX_KG` |
| Private Python members | leading underscore | `_round_to_resolution` |
| TS variables / functions | camelCase | `liveWeight`, `fetchBatches` |
| TS types / interfaces | PascalCase (no `I` prefix) | `Batch`, `RecipeComponent` |
| React components | PascalCase | `BatchQueue`, `WeightReadout` |
| React hooks | camelCase with `use` | `useLiveWeight` |
| Booleans | `is` / `has` / `can` prefix | `isWithinTolerance`, `canConfirm` |
| Event handlers | `handleX` inside, `onX` as prop | `handleConfirm`, `onConfirm` |
| JSON fields over the API | camelCase | `actualWeight`, `batchId` |

**Domain vocabulary (ubiquitous language)**: use the Product Brief glossary terms exactly — batch, recipe, component, dyestuff, lot, container, tare, tolerance, surplus, override, compensation, precision scale, floor (heavy-duty) scale. Do not invent synonyms (e.g. not "job item" for component).

**File Naming**:
- React components: `PascalCase.tsx`
- Other TS files: `kebab-case.ts`
- Python: `snake_case.py`
- Tests: Python `test_<subject>.py`; TS `<Subject>.test.tsx` / `<subject>.test.ts`; E2E `<flow>.spec.ts`

Pydantic schemas use an alias generator so Python stays snake_case while JSON is camelCase.

## File Organization

**Pattern**: domain-driven backend (layered), feature-based frontend

**Structure**:
```text
weighingms/
├── package.json              # root scripts: `npm run dev` starts backend + frontend
├── pyproject.toml            # Poetry (backend)
├── src/
│   ├── weighingms/           # WeighingMS backend
│   │   ├── domain/           #   entities, value objects, business rules — no FastAPI/SQLAlchemy imports
│   │   ├── application/      #   use cases orchestrating domain + ports
│   │   ├── infrastructure/   #   SQLAlchemy persistence, OrgaTEX adapter, device adapters
│   │   └── api/              #   FastAPI routers + Pydantic schemas
│   └── dummy_systems/        # training substitutes: orgatex/, scale/, scanner/, printer/
├── frontend/                 # React + Vite
│   └── src/
│       ├── features/         #   batch-queue/, weighing/, ticket/
│       ├── shared/           #   shared components, hooks, utils
│       └── api/              #   typed API client + generated OpenAPI types
├── tests/                    # pytest: unit/, integration/, api/
├── playwright/               # E2E specs, config, HTML report
└── data/                     # seed JSON; SQLite files are git-ignored
```

**Conventions**:
- Backend tests: separate `tests/` tree mirroring `src/`
- Frontend tests: co-located next to the component
- E2E tests: `playwright/`
- Types: co-located; generated API types in `frontend/src/api/`
- Index files: allowed only as a feature's public entry point; no deep barrel chains
- `domain/` must not import from `infrastructure/`, `api/` or `dummy_systems/`
- `weighingms` must not import from `dummy_systems` — it reaches dummies only over HTTP through adapters

## Testing Strategy

**Framework**: pytest (backend), Vitest + React Testing Library (frontend), Playwright Test with TypeScript runner (E2E)
**Coverage Target**: every business rule has explicit tests; ≥80% backend line coverage (pytest-cov)

**Test Types**:

| Type | Tool | When to Use |
|------|------|-------------|
| Unit | pytest | Domain rules: tolerance (incl. boundaries such as 93.4 / 93.5 / 94.0 / 94.5 / 94.6 g), scale selection (≤3 kg precision, >3 kg heavy-duty), component progression, batch completion, overshoot rule |
| API / integration | pytest + FastAPI `TestClient` | Every Dummy API and WeighingMS endpoint; fresh temporary SQLite database per test |
| Frontend unit | Vitest + React Testing Library | Components and view states, e.g. Confirm enabled/disabled per tolerance state |
| E2E | Playwright Test | Full B-24187 flow and failure scenarios; HTML report and video recording enabled |

**Conventions**:
- Test naming: Python `test_<behaviour>_when_<condition>`; TS `it('<does something> when <condition>')`
- Test structure: Arrange–Act–Assert
- Mock strategy: no mocks for external systems — the Dummy APIs are the test doubles. They must be deterministic (tests can set an exact weight; no reliance on timing or randomness) and able to simulate failures (scale, OrgaTEX, printer unavailable)
- Test data: the prototype's training scenario (batch B-24187) as a shared fixture

**Commands**:
- `npm run dev` — start the application (backend + frontend)
- `npm run check` — format check, lint, type check, backend and frontend unit/API tests
- `npm run test:e2e` — Playwright suite

## Error Handling

**Pattern**: throw (exceptions in Python; thrown errors caught at the API client boundary in TS)

**Custom Errors**: yes — domain exceptions derive from `DomainError` and carry a stable `code`, e.g. `OUT_OF_TOLERANCE`, `BATCH_NOT_RELEASED`, `SCALE_UNAVAILABLE`, `BATCH_INCOMPLETE`.

**API Errors**: one global FastAPI exception handler; every error response has the shape
```json
{"error": {"code": "SCALE_UNAVAILABLE", "message": "Human-readable text", "details": {}}}
```
Status codes: 400 invalid request, 404 not found, 409 conflicting state, 422 validation, 503 dependency unavailable (OrgaTEX, scale, printer). Stack traces are never sent to the client.

**Frontend**: a typed API client converts error bodies into plain-language operator messages (C-05); an error boundary per view; errors are never silently swallowed.

**Fail safe**: when in doubt (scale disconnected, reading unstable, dependency unavailable) block confirmation (IR-13).

## Logging

**Tool**: Python standard `logging`
**Format**: human-readable text to the console, with a request ID on each line

**Levels**:

| Level | Usage |
|-------|-------|
| ERROR | A failure that needs attention (dependency down, unexpected exception) |
| WARNING | Unexpected but handled (retry, out-of-tolerance attempt, rejected action) |
| INFO | Business events and API requests |
| DEBUG | Technical detail, including individual weight readings |

**Rules**:
- Always log: API requests (method, path, status, duration); every call to OrgaTEX, scale, scanner and printer with its outcome (IR-09); business events (batch selected, component confirmed, override, batch completed, consumption posted, ticket printed)
- Never log: supervisor PINs or other secrets
- High-frequency weight readings only at DEBUG
- Logs are diagnostic only; privileged actions are recorded as `AUDIT_EVENT` rows in the database, not in logs

## Project-Specific Rules
- **Quantities over the API** are decimal strings with a unit, e.g. `{"value": "94.0", "unit": "g"}`, never JSON numbers.
- **Business rules live only in the backend domain** (tolerance, scale selection, compensation/overshoot, completion). The UI renders the backend's evaluation (e.g. `canConfirm`) and never re-implements the rules. Display-only arithmetic (e.g. a progress bar width) is allowed in the UI.
- **Configurable rules**: scale-selection threshold and tolerance rules come from configuration/data, not constants buried in code (Project Requirement §5.3, §6 Step 6).
- **API types are generated**: `openapi-typescript` generates frontend types from FastAPI's `/openapi.json`; regenerate whenever the API changes; do not hand-write API types.
