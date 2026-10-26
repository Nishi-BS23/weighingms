---
stage: plan
bolt: 005-weighing-station-ui
created: 2026-10-26T07:01:30Z
---

## Implementation Plan: 006-weighing-station-ui (bolt 1 of 4)

### Objective
Scaffold the React + TypeScript operator terminal, reproduce the prototype's device frame and chrome (top bar, step indicator, live status strip, clock) plus the training panel outside the device, and deliver **Screen 1 · Select batch** wired to the WeighingMS API (Workbook Step 19). `npm run dev` starts dummy + API + UI.

### 1. What will change
A new `frontend/` application; the root `dev` and `check` scripts include it; API types are generated from FastAPI's OpenAPI schema.

### 2. Files to be created / modified
- `frontend/package.json`, `index.html`, `vite.config.ts` (proxy `/api` → `:8000`, Vitest jsdom), `tsconfig.json` (strict), `eslint.config.js`, `.prettierrc.json`
- `frontend/src/main.tsx`, `App.tsx` — station state (step, selected batch, recipe)
- `frontend/src/api/schema.d.ts` (generated), `api/client.ts` (typed fetch, standard error body → `ApiError`), `api/types.ts`
- `frontend/src/shared/use-polling.ts`, `shared/time.ts`, `shared/messages.ts` (error code → plain message; extended in bolt 010)
- `frontend/src/styles/station.css` — prototype design tokens and layout (CSS ported; JavaScript not copied)
- `frontend/src/features/chrome/` — `DeviceFrame.tsx`, `TopBar.tsx`, `StepIndicator.tsx`, `StatusStrip.tsx`, `TrainingPanel.tsx`
- `frontend/src/features/batch-queue/` — `BatchQueueScreen.tsx`, `ScanPrompt.tsx`, `QueueTable.tsx`, `use-scanner.ts`
- `frontend/src/features/weighing/RecipePreview.tsx` — read-only recipe view reached after selection (full Screen 2 in bolt 008)
- Root `package.json` — `dev:web`, `check:web`, `gen:api`, `setup` (modified); `scripts/dump_openapi.py`
- Tests: `*.test.tsx` next to components

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 001-station-shell-and-chrome | FR-33, FR-24 (display), FR-19 (display), FR-29 (panel) |
| 002-batch-queue-screen | FR-30, FR-1 |
| 003-select-batch-by-touch-or-scan | FR-30, FR-2 |

### 4. APIs involved (WeighingMS only — the browser never calls a dummy)
`GET /api/batches`, `GET /api/batches/{id}`, `GET /api/batches/{id}/recipe`, `GET /api/devices/status` (1 s poll), `GET /api/scanner/scans?after=` (300 ms poll on Screen 1), `GET /api/operators/current` (tolerated as absent until bolt 006), `/api/training/*` (panel).

### 5. How it will be tested
- Vitest + React Testing Library with a fetch stub: status strip states, step-indicator reachability, queue rows from the API (no hard-coded batches), non-selectable reason, OrgaTEX-unavailable message + Retry, keyboard-wedge scan selects, scanner-unavailable prompt.
- `tsc --noEmit`, ESLint (type-checked rules), Prettier check.
- Manual run of `npm run dev`: Screen 1 in the browser; network evidence of the three batch calls on selection (Workbook STEP-19).

### Technical Approach
- Plain CSS with the prototype's tokens and class names for visual fidelity; the device screen stays dark in both themes.
- Containers fetch through `api/client.ts`; presentational components take props (easy to test).
- No business rules in the UI: selectability, scales, bands come from the API.
- Known sequencing: the operator chip reads `GET /api/operators/current` (delivered in bolt 006) and shows "Operator —" until then; the badge dialog and `POST /api/sessions` are wired in bolt 008.

### Acceptance Criteria
- [ ] `npm run dev` prints the UI URL and serves Screen 1
- [ ] Queue rows come from `GET /api/batches`; no batch literals in UI code
- [ ] Selecting B-24187 (touch or scan) calls `/api/batches/B-24187` and `/api/batches/B-24187/recipe` and shows the recipe
- [ ] Non-selectable/unknown codes explained; OrgaTEX down → message + Retry; scanner down → touch hint
- [ ] Device frame, top bar, step indicator, status strip and training panel match the prototype
- [ ] `npm run check` green (backend + frontend)

### Checkpoint — plan review (delegated, self-validated)
Covers all three stories; consumes only agreed WeighingMS endpoints; preserves the prototype's look; testable. **APPROVE PLAN.**
