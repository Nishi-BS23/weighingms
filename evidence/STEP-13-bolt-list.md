# Step 13: WeighingMS Bolts (`/specsmd-construction-agent` bolt-list)

| Bolt ID | Unit | Type | Stories | Depends on | Status | Description |
|---------|------|------|---------|------------|--------|-------------|
| 001-training-substitutes | 001-training-substitutes | Simple | 3 | — | planned · Ready ✅ | Create the backend project skeleton (Poetry, ruff, mypy, pytest, root `package.json` with `npm run dev`) and t |
| 002-training-substitutes | 001-training-substitutes | Simple | 4 | 001-training-substitutes | planned · 🚫 waiting | Add the Dummy Scale (two scales, simulation profiles, tare, calibration), Dummy Scanner, Dummy Printer, failur |
| 003-orgatex-integration | 003-orgatex-integration | Simple | 3 | 001-training-substitutes | planned · 🚫 waiting | Create the WeighingMS backend app (:8000) with configuration, error handling and logging conventions, the `Org |
| 004-device-integration | 004-device-integration | Simple | 4 | 002-training-substitutes, 003-orgatex-integration | planned · 🚫 waiting | Implement `ScalePort` and `ScannerPort` adapters, device status aggregation and the training passthrough endpo |
| 005-weighing-station-ui | 006-weighing-station-ui | Simple | 3 | 003-orgatex-integration, 004-device-integration | planned · 🚫 waiting | Scaffold the React frontend, reproduce the device chrome and training panel, and deliver Screen 1 (batch queue |
| 006-weighing-station | 002-weighing-station | DDD | 5 | 003-orgatex-integration, 004-device-integration | planned · 🚫 waiting | Model the weighing domain and deliver the core session slice: start/resume, scale rule, tolerance evaluation,  |
| 007-weighing-station | 002-weighing-station | DDD | 6 | 006-weighing-station | planned · 🚫 waiting | Deliver confirmation with immutable records, the overshoot rule decided at Workbook Step 24, supervisor overri |
| 008-weighing-station-ui | 006-weighing-station-ui | Simple | 4 | 005-weighing-station-ui, 007-weighing-station | planned · 🚫 waiting | Deliver Screen 2: recipe rail, live weighing panel, actions and dialogs, surplus panel — all driven by the ses |
| 009-ticket-printing | 005-ticket-printing | Simple | 3 | 007-weighing-station, 002-training-substitutes | planned · 🚫 waiting | Compose the weighing ticket from the completed session, print it through the printer adapter, and mark reprint |
| 010-weighing-station-ui | 006-weighing-station-ui | Simple | 4 | 008-weighing-station-ui, 009-ticket-printing | planned · 🚫 waiting | Deliver Screen 3 (summary, per-component results, write-back status + retry, ticket preview and print, next ba |
| 011-weighing-station-ui | 006-weighing-station-ui | Simple | 2 | 010-weighing-station-ui | planned · 🚫 waiting | Prove the product: Playwright end-to-end run of B-24187 with report and video, failure-scenario suite, and the |

**Total**: 11 · In progress: 0 · Planned: 11 · Completed: 0

**Next executable bolt**: `001-training-substitutes` (unit `001-training-substitutes`) — the only bolt with no unmet dependencies.
