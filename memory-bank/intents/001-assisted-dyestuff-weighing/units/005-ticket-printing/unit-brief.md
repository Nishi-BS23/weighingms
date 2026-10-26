---
unit: 005-ticket-printing
intent: 001-assisted-dyestuff-weighing
phase: inception
status: complete
unit_type: backend
default_bolt_type: simple-construction-bolt
created: 2026-10-26T06:40:00.000Z
updated: 2026-10-26T06:40:00.000Z
---

# Unit Brief: Ticket & Printing

## Purpose

Produce the weighing ticket that accompanies the container to the dyeing machine (BR-15): compose it from the completed session, show the same content as a preview, print it on the (dummy) printer, and mark reprints.

## Scope

### In Scope
- Ticket model and text layout following the prototype (configurable header and fields)
- Barcode value (batch ID) — rendering left to the UI/printer
- `PrinterPort` implementation for the Dummy Printer
- Endpoints: `GET /api/sessions/{sessionId}/ticket` (preview), `POST /api/sessions/{sessionId}/ticket/print`
- Reprint marking and REPRINT audit event; printer failure → 503 `PRINTER_UNAVAILABLE`

### Out of Scope
- Label design, printer language, real printer (UQ-11)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-18 | Ticket generation | Must |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| Ticket | Printable record | header, batchId, orderRef, machineRef, shadeCode, printedAtLocal, operatorName, lines[], resultLine, barcodeValue, reprint |
| TicketLine | One component | shortName, target, actual, unit |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| compose | Build ticket from completed session | sessionId | Ticket |
| print | Send to printer; first = original, later = REPRINT | sessionId | ticketId, printedAt, reprint |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 3 |
| Must Have | 2 |
| Should Have | 0 |
| Could Have | 1 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001-compose-weighing-ticket | Compose the weighing ticket | Must | Planned |
| 002-print-ticket | Print the ticket on the printer | Must | Planned |
| 003-reprint-ticket | Reprint marked as reprint | Could | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 002-weighing-station | Completed session, records, operator |
| 001-training-substitutes | Dummy Printer contract |

### Depended By
| Unit | Reason |
|------|--------|
| 006-weighing-station-ui | Preview and print |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| Ticket printer (Dummy) | Printing | Low |

---

## Technical Context

### Suggested Technology
Application service in `src/weighingms/application/tickets.py`; `httpx` printer adapter; ticket config (header text, short names) in the configuration file.

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| Dummy Printer | API | REST/JSON |
| UI | API | REST/JSON |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Print history (ticketId, reprint, printedAt) | SQLite `weighingms.db` | Training volume | Permanent |

---

## Constraints

- Ticket only for COMPLETED sessions (`SESSION_NOT_COMPLETED` otherwise).
- Short component names configurable (e.g. "Remazol Brill. Blue RSPL" → "Blue RSPL", "Sodium Sulphate" → "Na2SO4").

---

## Success Criteria

### Functional
- [ ] Ticket content matches the prototype fields for B-24187
- [ ] Print → Dummy Printer stores ticket, ID returned
- [ ] Printer down → clear error, completion unaffected; retry works
- [ ] Second print marked REPRINT

### Non-Functional
- [ ] Print round trip < 1 s locally

### Quality
- [ ] Code coverage > 80%
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| 009-ticket-printing | Simple | 001, 002, 003 | Ticket composition, printing, reprint |

---

## Notes

The prototype states "Label content is invented" — keep content in configuration (TA-15).
