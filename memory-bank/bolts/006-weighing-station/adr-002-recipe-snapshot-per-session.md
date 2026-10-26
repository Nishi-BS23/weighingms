---
bolt: 006-weighing-station
created: 2026-10-26T07:14:08Z
status: accepted
superseded_by: null
---

# ADR-002: Snapshot the recipe (with scale and band) when a weighing session starts

## Context

Recipes are owned by OrgaTEX and may change; Brief BR-14 requires reconstructing exactly what the operator was asked to weigh, and BR-16 requires weighing in progress to continue through an OrgaTEX outage.

## Decision

At session start WeighingMS stores a JSON snapshot of the recipe — each component's target, tolerance band, selected scale, lot and identity — on the session. All later steps use the snapshot, never OrgaTEX.

## Rationale

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| Read the recipe from OrgaTEX on every step | Always current | Fails during outages; history changes when the recipe changes | Violates BR-14, BR-16 |
| Normalised recipe tables | Queryable | More tables for read-only data that never changes after start | Snapshot is simpler and sufficient |

## Consequences

### Positive

- Weighing continues when OrgaTEX drops after start (TA-13).
- Records and tickets always match what was shown.

### Negative

- A recipe correction in OrgaTEX after start is not picked up (by design; the batch must be restarted by OrgaTEX).

### Risks

- Snapshot schema evolution — mitigated by versioning the snapshot payload (`snapshotVersion`).

## Related

- **Stories**: 002-weighing-station/001-start-or-resume-weighing-session, 010-activate-component-weighing-context
- **Standards**: data-stack (decimal-as-text applies inside the JSON as strings)
- **Previous ADRs**: none
