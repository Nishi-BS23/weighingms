---
stage: test
bolt: 006-weighing-station
created: 2026-10-26T08:49:58Z
---

## Test Report: 002-weighing-station (core session slice)

### Summary

- **Unit Tests**: 47/47 passed (tolerance evaluation incl. Workbook Step 22, display scale, aggregate invariants, containers, operators)
- **Integration Tests**: 9/9 passed (Alembic migration, WAL + synchronous=FULL, aggregate round trip with exact decimals, open-session uniqueness, audit/state)
- **API Tests**: 20/20 passed (sessions, live evaluation, scale switch, tare/re-tare, offline/calibration, operators, training simulation/reset, training mode off)
- **Security Tests**: training routes absent when `training_mode = false` (ADR-003); operator change audited
- **Performance**: live endpoint uses one indexed session read + one scale read (~2 ms dummy read measured in bolt 004)
- **Whole backend**: 174/174 passed, coverage 97.8%; ruff + mypy --strict clean; 0 ResourceWarnings

### Acceptance Criteria Validation

- ✅ **001-start-or-resume-weighing-session**: QUEUED → session with recipe snapshot, operator, first component ACTIVE, OrgaTEX WEIGHING; reselect resumes (200, same session, active kept); WEIGHED → 409 `BATCH_NOT_SELECTABLE`; unknown → 404; OrgaTEX down with no session → 503; operator current/sign-in/unknown badge + OPERATOR_CHANGE audit; session survives app restart
- ✅ **002-automatic-scale-selection**: precision ×3 / floor ×2; 3.000 kg vs 3.001 kg; configurable threshold (bolt 003 tests) applied in the session snapshot
- ✅ **003-tolerance-evaluation**: 93.4 ✗ / 93.5 ✓ / 94.0 ✓ / 94.5 ✓ / 94.6 ✗; NEAR ≥ 90%; remaining/surplus/surplus % (96.4 g → +2.4 g, +2.6%); status texts; kg components; default tolerance band; OFFLINE when scale down; calibration expired blocks confirm
- ✅ **007-component-progression**: fresh session → first ACTIVE; activating another returns previous to PENDING; only one ACTIVE; DONE not activatable (409); completed session not activatable
- ✅ **010-activate-component-weighing-context**: Yellow → C-12, 214.0 g, scale-3kg, band 93.5–94.5, display max 125.0 g; Sodium Sulphate → D-03, 1.850 kg, scale-32kg, kg; activation tares the scale (net 0.0); re-tare → 0; live endpoint fields

### Issues Found

- Defect fixed: SQLite engines were never disposed (ResourceWarning "unclosed database"); containers now close their engine on application shutdown and tests close theirs.

### Recommendations

- Bolt 007 adds confirmation/override/quit/completion on this aggregate; the Step 24 overshoot decision must be taken before implementing story 005.
- Frontend API types must be regenerated (`npm run gen:api`) in bolt 008 to pick up session and operator endpoints.

### Stage checkpoint (delegated, self-validated)

All tests pass and every acceptance criterion of the five stories is verified. **Approved** — bolt complete.
