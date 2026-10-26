---
bolt: 007-weighing-station
created: 2026-10-26T08:51:49Z
status: accepted
superseded_by: null
---

# ADR-004: Over-dosed components are blocked and recovered, never recalculated

## Context

The prototype proposes recalculating the remaining components after an over-dose; the Brief marks this meaning of "surplus compensation" as its most likely misunderstanding (A-08, Q25/Q26). Workbook Step 24 requires an explicit decision.

## Decision

An over-dosed component stays unconfirmed. Recovery is by removing excess back into the band, emptying and re-taring to weigh again, or a supervisor override (PIN + reason) recorded as OVERRIDDEN with the surplus. WeighingMS never changes recipe targets. Full decision record: `evidence/STEP-24-overshoot-decision.md`.

## Rationale

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| Proportional compensation (prototype proposal) | Preserves shade ratio if the assumption is right | Modifies recipe quantities outside OrgaTEX (C-01); rests on unconfirmed A-08; large scope | Not an approved business rule |
| Accept over-dose with surplus recorded, no authorisation | Fast | Violates BR-07 | Unsafe |

## Consequences

### Positive

- Satisfies BR-07, BR-08, BR-13 with minimal scope; every exception is attributable.

### Negative

- An accepted over-dose is not corrected automatically; the shade impact is handled by people.

### Risks

- FCI may require compensation — it would be added as a new story with its own approval flow; the evaluation's `allowedActions`/`guidance` are the extension point.

## Related

- **Stories**: 002-weighing-station/005-overshoot-handling, 006-supervisor-override; 006-weighing-station-ui/007-overshoot-surplus-panel
- **Standards**: none
- **Previous ADRs**: ADR-001 (evaluation in the backend)
