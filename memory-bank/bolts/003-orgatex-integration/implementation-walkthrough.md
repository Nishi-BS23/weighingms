---
stage: implement
bolt: 003-orgatex-integration
created: 2026-10-26T06:52:26Z
---

## Implementation Walkthrough: 003-orgatex-integration

### Summary

The WeighingMS backend exists on port 8000 with configuration, a standard error body and request-ID logging. All OrgaTEX interaction goes through one HTTP adapter behind `OrgatexPort`; the UI-facing batch endpoints return the queue with selectability and fabric/lot text, and the recipe enriched with each component's automatic scale and tolerance band. `npm run dev` now starts the dummy service and the API together.

### Structure Overview

Hexagonal layering: `domain` (exact quantities, scale-selection policy, tolerance bands, error types) has no framework imports; `application` defines the ports and the batch service; `infrastructure/orgatex` parses the external wire contract and maps it to port DTOs; `api` holds the composition root (container), routers, schemas, error handlers and middleware. Business configuration is read from `config/station.toml`; wiring from environment variables.

### Completed Work

- [x] `config/station.toml` - station identity, selectable statuses, scale threshold and scale labels, default tolerance rule, ticket short names
- [x] `src/weighingms/config.py` - settings loader (environment + TOML) into typed domain policies
- [x] `src/weighingms/logging_setup.py` - console log format with request ID
- [x] `src/weighingms/domain/quantity.py` - exact g/kg quantity, conversion, display precision, comparisons
- [x] `src/weighingms/domain/scale_selection.py` - scale definitions and threshold policy
- [x] `src/weighingms/domain/tolerance.py` - inclusive tolerance band; default rule with per-class minimum
- [x] `src/weighingms/domain/errors.py` - `DomainError` hierarchy with stable codes and HTTP status
- [x] `src/weighingms/application/ports.py` - `OrgatexPort`, port DTOs, `OrgatexUnavailable`, `OrgatexBadData`
- [x] `src/weighingms/application/batches.py` - queue/batch/recipe service, selectability reasons, fabric/lot text, recipe enrichment
- [x] `src/weighingms/infrastructure/orgatex/contract.py` - Dummy OrgaTEX wire models
- [x] `src/weighingms/infrastructure/orgatex/http_adapter.py` - reads, status write-back, idempotent consumption posting, error translation, call logging, last-contact time
- [x] `src/weighingms/api/app.py` - app factory and health endpoint
- [x] `src/weighingms/api/container.py` - composition root (httpx client with 2 s timeout)
- [x] `src/weighingms/api/errors.py` - standard error body for domain, validation, HTTP and unexpected errors (no stack traces to clients)
- [x] `src/weighingms/api/middleware.py` - request ID header and request logging (polling endpoints at DEBUG)
- [x] `src/weighingms/api/schemas.py` - camelCase response models with decimal-string quantities
- [x] `src/weighingms/api/batches.py` - `GET /api/batches`, `/api/batches/{id}`, `/api/batches/{id}/recipe`
- [x] `package.json` - `dev` runs `dev:dummy` and `dev:api`

### Key Decisions

- **Scale and band in the recipe response**: the rail and header can show "3 kg precision" and "TOLERANCE ±0.5 g (93.5 – 94.5)" before a session starts, computed by domain policies, never by the UI.
- **Unknown OrgaTEX statuses are kept**: shown in the queue but not selectable ("Batch status is not supported.").
- **Error translation in the adapter**: transport errors/timeouts/5xx → `ORGATEX_UNAVAILABLE` (503); 404 with a batch → `BATCH_NOT_FOUND`; malformed data → `ORGATEX_BAD_DATA` (502).
- **Polling endpoints log at DEBUG**: keeps INFO logs readable when the UI polls several times per second.

### Deviations from Plan

None.

### Dependencies Added

None.

### Developer Notes

Smoke run via `npm run dev`: queue and recipe returned through the adapter; B-24187 bands 1234.0–1246.0 g, 384.0–388.0 g, 93.5–94.5 g, 23.880–24.120 kg, 9.552–9.648 kg with scales precision ×3 / floor ×2; OrgaTEX toggled off → 503 `ORGATEX_UNAVAILABLE`; each OrgaTEX call logged with status and duration.

### Stage checkpoint (delegated, self-validated)

Deliverables complete, standards followed, lint/type checks clean. **Approved** — proceed to Test.
