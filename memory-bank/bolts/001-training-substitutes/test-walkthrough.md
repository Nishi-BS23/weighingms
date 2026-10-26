---
stage: test
bolt: 001-training-substitutes
created: 2026-10-26T06:42:13Z
---

## Test Report: 001-training-substitutes

### Summary

- **Tests**: 18/18 passed
- **Coverage**: 97% (backend total); `orgatex/store.py` 90% — uncovered lines are the concurrent-duplicate race path and `reset()` (exercised in bolt 002)
- **Static checks**: `ruff format --check`, `ruff check`, `mypy --strict` — all clean (`npm run check`)

### Test Files

- [x] `tests/api/dummy_systems/test_orgatex_api.py` - queue, status filter, detail, 404s, exact B-24187 recipe, quantities as strings, seed consistency through the API, missing tolerance, consumption store/idempotency/validation, status write-back, invalid status, unknown route error body
- [x] `tests/unit/dummy_systems/test_orgatex_seed.py` - real seed loads; component-count, recipe-ownership and sequence errors are rejected
- [x] `tests/conftest.py` - isolated app per test (temporary SQLite, fixed clock)

### Acceptance Criteria Validation

- ✅ **`/api/batches` lists B-24187, B-24188, B-24190, B-24191 with all fields**: test + curl (evidence/STEP-18-api-tests.txt, HTTP 200)
- ✅ **`/api/batches/B-24187` returns SO-9931, JET-04, 100% CTN knit, 480 kg, Teal 4C, 5, QUEUED**: test + curl (HTTP 200)
- ✅ **`/api/batches/B-24187/recipe` returns the 5 prototype components exactly**: test compares every value + curl (HTTP 200)
- ✅ **Unknown batch → 404 with standard error body**: test + curl (HTTP 404, `BATCH_NOT_FOUND`)
- ✅ **Consumption posting idempotent and retrievable; status PATCH works**: tests
- ✅ **`npm run dev` starts the dummy service; `npm run check` green**: smoke run + check output

### Issues Found

- Defect found and fixed during this stage: the consumption receipt read the row ID after the SQLAlchemy session closed (`DetachedInstanceError`). The ID is now generated before the insert.

### Notes

- Starlette emits a deprecation warning about `httpx` in its test client; harmless for now, revisit if it becomes an error.
- Evidence: `evidence/STEP-17-dummy-data.json` (seed), `evidence/STEP-18-api-tests.txt` (curl results).

### Stage checkpoint (delegated, self-validated)

All tests pass and every acceptance criterion is verified. **Approved** — bolt complete.
