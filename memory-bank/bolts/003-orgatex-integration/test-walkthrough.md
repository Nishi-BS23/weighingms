---
stage: test
bolt: 003-orgatex-integration
created: 2026-10-26T06:54:18Z
---

## Test Report: 003-orgatex-integration

### Summary

- **Tests**: 89/89 passed (38 new in this bolt)
- **Coverage**: 98% (backend total)
- **Static checks**: ruff format/lint and mypy --strict clean (`npm run check`)

### Test Files

- [x] `tests/unit/weighingms/test_quantity.py` - exact g/kg conversion, display precision, cross-unit arithmetic/comparison, no float drift
- [x] `tests/unit/weighingms/test_scale_selection.py` - all prototype components, 3.000 kg / 3000.0 g / 3.001 kg boundary, PDF examples (0.250, 3.500 kg), configurable threshold
- [x] `tests/unit/weighingms/test_tolerance_band.py` - inclusive band (93.4/93.5/94.5/94.6 g), kg band, default rule 0.5%, per-class minimum, unit conversion of tolerance
- [x] `tests/integration/weighingms/test_orgatex_adapter.py` - real adapter against the real Dummy OrgaTEX: queue/recipe mapping, last contact, 404 → BatchNotFound, unavailable (failure injection) and connection refused → OrgatexUnavailable, status write-back, idempotent consumption posting, malformed data and 4xx → OrgatexBadData
- [x] `tests/api/weighingms/test_batches_api.py` - WeighingMS endpoints: queue with fabric/lot + selectability + request ID header, WEIGHED not selectable with reason, detail, recipe enriched with scale + band for all 5 components, default tolerance for B-24190 Soda Ash, 404, 503 with plain message, standard error body, health
- [x] `tests/conftest.py` - dummy app in-process; WeighingMS wired to it through the real HTTP adapter

### Acceptance Criteria Validation

- ✅ **UI-facing `GET /api/batches` returns the four batches with fabric/lot and selectability via the adapter**
- ✅ **Recipe bands and scales for B-24187 exactly as the prototype** (1234.0–1246.0 g … 9.552–9.648 kg; precision ×3, floor ×2)
- ✅ **OrgaTEX down → 503 `ORGATEX_UNAVAILABLE` with a plain message; unknown batch → 404**
- ✅ **Status write-back and idempotent consumption posting through the adapter**
- ✅ **Every OrgaTEX call logged with method, path, status, duration** (verified in the `npm run dev` smoke log)
- ✅ **`npm run dev` starts dummy + API; `npm run check` green**

### Issues Found

None.

### Notes

The adapter's only unit-test doubles are `httpx.MockTransport` cases for malformed data and 4xx responses that the dummy never produces; all other behaviour is tested against the real dummy.

### Stage checkpoint (delegated, self-validated)

All tests pass; all acceptance criteria verified. **Approved** — bolt complete.
