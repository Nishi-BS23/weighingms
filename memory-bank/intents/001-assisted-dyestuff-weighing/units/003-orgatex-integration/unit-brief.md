---
unit: 003-orgatex-integration
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
unit_type: backend
default_bolt_type: simple-construction-bolt
created: 2026-10-26T06:40:00.000Z
updated: 2026-10-26T06:40:00.000Z
---

# Unit Brief: OrgaTEX Integration

## Purpose

Confine all OrgaTEX interaction to one replaceable adapter (Brief IR-07) and expose the batch queue, batch detail and recipe to the WeighingMS UI in WeighingMS's own model. Post batch status and actual consumption back idempotently.

## Scope

### In Scope
- `OrgatexPort` interface (defined with the domain) and its HTTP implementation against the Dummy OrgaTEX
- WeighingMS endpoints: `GET /api/batches`, `GET /api/batches/{batchId}`, `GET /api/batches/{batchId}/recipe` (mapped model, decimal strings, scale assignment and tolerance band added by the domain policies)
- Status write-back (WEIGHING/WEIGHED) and consumption posting with idempotency key; error translation to `ORGATEX_UNAVAILABLE`; last successful contact time for the status strip
- Logging of every OrgaTEX call with outcome (IR-09)

### Out of Scope
- Deciding *when* to write back (weighing-station completion)
- Real OrgaTEX interface (UQ-01)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Batch queue | Must |
| FR-3 | Recipe loading | Must |
| FR-4 | Component identification | Must |
| FR-17 | OrgaTEX write-back | Must |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| BatchSummary | Queue row | batchId, orderRef, machineRef, fabricDesc, shadeCode, componentCount, status, selectable |
| BatchDetail | Batch header | + fabricWeightKg, recipeId, releasedAt |
| Recipe | Components with identity data | recipeId, shadeCode, version, components[] |
| ConsumptionPayload | Write-back body | batchId, sessionId (idempotency key), completedAt, lines[] |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| listBatches | Queue for the station | — | BatchSummary[] + receivedAt |
| getBatch | Header | batchId | BatchDetail |
| getRecipe | Recipe | batchId | Recipe |
| setBatchStatus | Status write-back | batchId, status | ack |
| postConsumption | Idempotent write-back | payload | ack (postedAt) |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 3 |
| Must Have | 3 |
| Should Have | 0 |
| Could Have | 0 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001-batch-queue-from-orgatex | Batch queue from OrgaTEX | Must | Planned |
| 002-batch-detail-and-recipe-from-orgatex | Batch detail and recipe from OrgaTEX | Must | Planned |
| 003-consumption-write-back | Status and consumption write-back | Must | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 001-training-substitutes | Dummy OrgaTEX contract for development and tests |

### Depended By
| Unit | Reason |
|------|--------|
| 002-weighing-station | Recipe snapshot, status and consumption write-back via port |
| 006-weighing-station-ui | Batch endpoints |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| OrgaTEX (Dummy in training) | Batches, recipes, write-back | High in reality (A-01/A-02); Low in training |

---

## Technical Context

### Suggested Technology
`httpx` client with short timeouts (2 s), Pydantic models for the external contract separate from WeighingMS DTOs, FastAPI router. Base URL from configuration (`ORGATEX_BASE_URL`, default `http://127.0.0.1:8100`).

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| Dummy OrgaTEX | API | REST/JSON |
| UI | API | REST/JSON |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Last OrgaTEX contact time | In memory | — | Process |

---

## Constraints

- No other WeighingMS module calls OrgaTEX.
- External contract types never leak into the domain.
- Write-back carries the session ID as idempotency key.

---

## Success Criteria

### Functional
- [ ] UI obtains the queue only via `GET /api/batches` (Workbook Step 19)
- [ ] OrgaTEX down → 503 `ORGATEX_UNAVAILABLE` with plain message
- [ ] Repeated consumption posting → one record in Dummy OrgaTEX

### Non-Functional
- [ ] Recipe endpoint < 300 ms locally (supports NFR-2)

### Quality
- [ ] Code coverage > 80%
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| 003-orgatex-integration | Simple | 001, 002, 003 | Adapter, batch endpoints, write-back |

---

## Notes

If the real OrgaTEX turns out to be OPC-UA, a database or file exchange, only this unit changes (Brief §10.1).
