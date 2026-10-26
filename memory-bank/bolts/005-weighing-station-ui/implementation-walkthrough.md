---
stage: implement
bolt: 005-weighing-station-ui
created: 2026-10-26T07:09:59Z
---

## Implementation Walkthrough: 006-weighing-station-ui (bolt 1 of 4)

### Summary

The operator terminal now exists as a React + TypeScript app (Vite) that reproduces the prototype's page chrome, dark device frame, top bar, step indicator and live status strip, with the prototype's simulation buttons in the top control bar and a separate training bar for simulated scans, failure injection and data reset. Screen 1 lists the OrgaTEX queue from the WeighingMS API and selects a batch by touch, keyboard-wedge entry or scanner, then shows the loaded recipe. `npm run dev` starts dummy service, API and UI.

### Structure Overview

`api/` holds the generated OpenAPI types and a typed fetch client that turns the standard error body into `ApiError`. `shared/` holds polling and one-shot loading hooks, time formatting and plain-language messages. Features are folders: `chrome` (frame pieces and training controls), `batch-queue` (Screen 1) and `weighing` (recipe preview until Screen 2 lands). `App.tsx` holds the step state and polls device status once for top bar and strip. Styling is plain CSS carrying the prototype's tokens and class names.

### Completed Work

- [x] `frontend/package.json`, `vite.config.ts`, `tsconfig.json`, `eslint.config.js`, `.prettierrc.json`, `.prettierignore`, `index.html` - toolchain (React 19, Vite 8, TS 5.9 strict, ESLint 10 type-checked, Prettier, Vitest 5 + jsdom 29)
- [x] `frontend/src/api/schema.d.ts` - generated from the WeighingMS OpenAPI schema
- [x] `frontend/src/api/client.ts`, `api/types.ts` - typed API client and type aliases
- [x] `frontend/src/shared/use-polling.ts`, `use-resource.ts`, `time.ts`, `messages.ts` - polling without overlap, one-shot loading, local time formatting, error-code → plain message
- [x] `frontend/src/styles/station.css` - prototype design ported (device stays dark in both themes) plus messages, dialogs, results table
- [x] `frontend/src/features/chrome/TopBar.tsx` - brand, station, batch crumb, operator chip
- [x] `frontend/src/features/chrome/StepIndicator.tsx` - workflow step indicator (reachability)
- [x] `frontend/src/features/chrome/StatusStrip.tsx` - device states with dots, OrgaTEX "LINKED HH:MM", language, live clock
- [x] `frontend/src/features/chrome/TrainingPanel.tsx` - simulation buttons (enabled when weighing, bolt 008) and training bar (scan, failure toggles, reset)
- [x] `frontend/src/features/batch-queue/BatchQueueScreen.tsx`, `ScanPrompt.tsx`, `QueueTable.tsx`, `use-scanner.ts` - Screen 1 with touch, keyboard-wedge and scanner selection, reasons for refused batches, OrgaTEX error + Retry, scanner-down hint
- [x] `frontend/src/features/weighing/RecipePreview.tsx` - read-only recipe after selection (replaced by Screen 2 in bolt 008)
- [x] `frontend/src/App.tsx`, `main.tsx` - app shell
- [x] `scripts/dump_openapi.py` - writes the OpenAPI schema for type generation
- [x] `package.json` (root) - `setup`, `dev` (dummy + api + web), `gen:api`, `check` (py + web)
- [x] `playwright/package.json` - Playwright installed early for visual checks and evidence (suites in bolt 011)

### Key Decisions

- **TypeScript 5.9.3, not 7**: typescript-eslint supports TypeScript < 6.1; type-checked linting is part of the coding standards.
- **jsdom 29**: jsdom 30 needs Node ≥ 22.22.2; the machine has 22.22.0.
- **Simulation buttons in the top control bar**: matches the prototype's layout; failure toggles and scan simulation sit in a separate training bar.
- **Keyboard-wedge field on Screen 1**: real wedge scanners type into the focused field; the dummy scanner path is polled as well.
- **No batch literals in UI code**: verified by grep (evidence/STEP-19-network.txt).

### Deviations from Plan

- The operator chip shows "Operator —" until `GET /api/operators/current` exists (bolt 006); the badge sign-in dialog moves to bolt 008 with the session wiring (as noted in the plan).

### Dependencies Added

- [x] react, react-dom - UI
- [x] vite, @vitejs/plugin-react, typescript, @types/* - build and types
- [x] eslint, @eslint/js, typescript-eslint, eslint-plugin-react-hooks, globals, prettier - quality
- [x] vitest, jsdom, @testing-library/* - component tests
- [x] openapi-typescript - generated API types
- [x] @playwright/test (playwright/) - browser evidence now, E2E later

### Developer Notes

Visual check against the prototype (headless Chromium screenshots): frame, top bar, scan prompt, queue table, status strip and clock match. Evidence: `evidence/STEP-19-batch-screen.png`, `STEP-19-after-selection.png`, `STEP-19-network.txt` (GET /api/batches → /api/batches/B-24187 → /api/batches/B-24187/recipe; scan path selects B-24191).

### Stage checkpoint (delegated, self-validated)

Deliverables complete; type check, lint and format clean; behaviour verified in a real browser. **Approved** — proceed to Test.
