---
last_updated: 2026-10-26T08:51:49Z
total_decisions: 4
---

# Decision Index

This index tracks all Architecture Decision Records (ADRs) created during Construction bolts.
Use this to find relevant prior decisions when working on related features.

## How to Use

**For Agents**: Scan the "Read when" fields below to identify decisions relevant to your current task. Before implementing new features, check if existing ADRs constrain or guide your approach. Load the full ADR for matching entries.

**For Humans**: Browse decisions chronologically or search for keywords. Each entry links to the full ADR with complete context, alternatives considered, and consequences.

---

## Decisions

### ADR-004: Over-dosed components are blocked and recovered, never recalculated
- **Status**: accepted
- **Date**: 2026-10-26
- **Bolt**: 007-weighing-station (002-weighing-station)
- **Path**: `bolts/007-weighing-station/adr-004-overshoot-block-and-recover.md`
- **Summary**: The prototype proposes recalculating remaining components after an over-dose (A-08). An over-dosed component stays unconfirmed and is recovered (remove excess, re-tare and re-weigh, or supervisor override); targets are never changed.
- **Read when**: working on overshoot, surplus, overrides, compensation, or tolerance exceptions

### ADR-003: Expose training endpoints only when training mode is enabled
- **Status**: accepted
- **Date**: 2026-10-26
- **Bolt**: 006-weighing-station (002-weighing-station)
- **Path**: `bolts/006-weighing-station/adr-003-training-mode-flag.md`
- **Summary**: The training build needs endpoints that drive the dummy systems. `/api/training/*` routes are mounted only when `station.training_mode = true`.
- **Read when**: adding training/simulation features, preparing a non-training deployment, reviewing API security

### ADR-002: Snapshot the recipe (with scale and band) when a weighing session starts
- **Status**: accepted
- **Date**: 2026-10-26
- **Bolt**: 006-weighing-station (002-weighing-station)
- **Path**: `bolts/006-weighing-station/adr-002-recipe-snapshot-per-session.md`
- **Summary**: Recipes are owned by OrgaTEX and may change. At session start WeighingMS stores a JSON snapshot of the recipe on the session.
- **Read when**: working on sessions, records, tickets, OrgaTEX outages, or recipe changes

### ADR-001: Deliver live weight to the UI by short polling of an evaluated reading
- **Status**: accepted
- **Date**: 2026-10-26
- **Bolt**: 006-weighing-station (002-weighing-station)
- **Path**: `bolts/006-weighing-station/adr-001-live-weight-by-polling.md`
- **Summary**: The tech stack left the live-weight transport open. The UI polls `GET /api/sessions/{id}/live` (~120 ms), which returns the evaluated reading.
- **Read when**: changing live weight display, scale integration, real-time transport, or tolerance evaluation placement
