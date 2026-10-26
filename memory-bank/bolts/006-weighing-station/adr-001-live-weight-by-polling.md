---
bolt: 006-weighing-station
created: 2026-10-26T07:14:08Z
status: accepted
superseded_by: null
---

# ADR-001: Deliver live weight to the UI by short polling of an evaluated reading

## Context

The tech stack left the live-weight transport open (polling vs WebSocket/SSE). NFR-1 requires the displayed weight to lag the scale by ≤ 200 ms, and the coding standards require tolerance evaluation in the backend, not the UI.

## Decision

The UI polls `GET /api/sessions/{id}/live` about every 120 ms. Each call reads the scale through `ScalePort` and returns the reading already evaluated (zone, remaining, surplus, canConfirm, status text).

## Rationale

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| WebSocket stream | Push, lowest latency | Connection management, reconnection logic, harder to test and to proxy; dummy scale computes readings lazily anyway | Complexity not needed on localhost for one station |
| Server-Sent Events | Simple push | Long-lived request per screen, still needs evaluation per tick, Vite proxy buffering edge cases | Same benefit as polling here, more moving parts |
| UI polls the raw scale and evaluates locally | Fewer backend calls | Business rules in the UI (violates standards); UI would need the band logic | Rejected by coding standards |

## Consequences

### Positive

- One request shape for UI, tests and evidence; trivially testable with the dummy.
- Evaluation logic stays in one place (domain).

### Negative

- ~8 requests per second while weighing (negligible on localhost; logged at DEBUG).

### Risks

- A real indicator streaming at ≥ 10 Hz over serial would be read by a background reader feeding the same `ScalePort`; the UI contract does not change.

## Related

- **Stories**: 002-weighing-station/003-tolerance-evaluation, 010-activate-component-weighing-context; 006-weighing-station-ui/005-live-weighing-panel
- **Standards**: tech-stack (transport decision recorded here)
- **Previous ADRs**: none
