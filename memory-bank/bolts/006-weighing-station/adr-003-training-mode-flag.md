---
bolt: 006-weighing-station
created: 2026-10-26T07:14:08Z
status: accepted
superseded_by: null
---

# ADR-003: Expose training endpoints only when training mode is enabled

## Context

The training build needs endpoints that drive the dummy systems (simulate dispense, failure injection, reset data). On a real station these would let anyone fake weights or wipe records.

## Decision

`/api/training/*` routes are mounted only when `station.training_mode = true` in `config/station.toml` (true in this training build). The UI hides the training panel when the routes are absent (`GET /api/training/availability` → 404).

## Rationale

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| Always mount training routes | Simplest | Dangerous outside training | Security |
| Separate training backend | Strong isolation | Duplicates wiring; the training panel needs session context | Overkill for the scope |

## Consequences

### Positive

- Same code base serves training and (future) production safely.

### Negative

- One configuration switch to remember when deploying for real.

### Risks

- Misconfiguration — mitigated by logging a WARNING at startup when training mode is on.

## Related

- **Stories**: 001-training-substitutes/007-failure-injection-and-reset; 004-device-integration/004-device-status-and-failure-detection
- **Standards**: tech-stack (security), coding-standards
- **Previous ADRs**: none
