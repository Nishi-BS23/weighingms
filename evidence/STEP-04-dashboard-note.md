# Step 4: Dashboard note

**Date:** 2026-10-26

## Observed problem
`npx specsmd@latest dashboard` (v0.1.74) started, but the page stayed on "Loading..."
(see `STEP-04-dashboard-loading.png`).

The dashboard API (`GET /api/snapshot`) returned:

```json
{"ok":false,"error":{"code":"NO_SUPPORTED_FLOW","message":"No supported flow detected. Expected one of: .specs-fire, memory-bank, specs"}}
```

Cause: the dashboard detects the AI-DLC flow by the presence of a `memory-bank/` folder,
which is normally only created by `project-init`. `--flow aidlc` does not help; the AI-DLC
parser also requires `memory-bank/` to exist.

## Decision (approved by participant)
Create the empty `memory-bank/` skeleton defined in `.specsmd/aidlc/memory-bank.yaml`:
`intents/`, `bolts/`, `standards/`, `operations/`.

No standards, project config or other content was written. The master agent still treats the
project as not initialized until `project-init` creates at least one standard.

## Result
`/api/snapshot` now returns `ok: true`, flow `aidlc`, with 0 intents, units, stories and bolts.
