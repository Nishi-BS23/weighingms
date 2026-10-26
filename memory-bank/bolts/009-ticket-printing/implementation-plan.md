---
stage: plan
bolt: 009-ticket-printing
created: 2026-10-26T09:06:01Z
---

## Implementation Plan: 005-ticket-printing

### Objective
Compose the weighing ticket from a completed session exactly as the prototype draws it, print it on the (dummy) ticket printer, and mark every later print as a reprint (FR-18, Workbook Step 27 backend).

### 1. What will change
- A ticket model and text layout in the domain; ticket header and station time zone in configuration.
- A printer port + HTTP adapter (extends the existing printer probe), a print log (migration 0003), and two endpoints.

### 2. Files to be created / modified
- `config/station.toml` — `[ticket] header`, `[station] timezone` (modified); `src/weighingms/config.py` (modified)
- `src/weighingms/domain/ticket.py` — ticket, lines, result line, text rendering (prototype layout)
- `src/weighingms/application/ports.py` — `PrinterPort`, `PrinterUnavailable`, `PrintStore` (modified)
- `src/weighingms/application/tickets.py` — `TicketService` (preview, print, reprint audit)
- `src/weighingms/infrastructure/devices/peripherals_adapter.py` — `HttpPrinterAdapter` (print + availability) (modified)
- `src/weighingms/infrastructure/persistence/migrations/versions/0003_print_log.py`, `tables.py`, `repositories.py` (`PrintLog`) (modified)
- `src/weighingms/api/tickets.py`; `api/container.py`, `api/app.py` (modified)
- Tests: `tests/unit/weighingms/test_ticket.py`, `tests/api/weighingms/test_tickets_api.py`

### 3. Requirements and stories implemented
| Story | Requirements |
|-------|--------------|
| 001-compose-weighing-ticket | FR-18 |
| 002-print-ticket | FR-18, FR-20 (printer failure) |
| 003-reprint-ticket | FR-18 (reprint), NFR-18 (audit) |

### 4. APIs involved
Provided: `GET /api/sessions/{id}/ticket` (preview), `POST /api/sessions/{id}/ticket/print`. Used: Dummy Printer `POST /api/tickets` (training contract; Workbook minimum).

### 5. How it will be tested
- Unit: ticket text for the prototype actuals equals the prototype ticket lines (header, BATCH/ORDER/MACHINE/SHADE/DATE/OPER., component columns, "ALL WITHIN TOLERANCE", batch ID); overridden line marked and result line "1 OVERRIDDEN"; REPRINT marker.
- API: preview for a completed session; 409 `SESSION_NOT_COMPLETED` before completion; print → stored in Dummy Printer with ticket ID; printer down → 503 `PRINTER_UNAVAILABLE`, completion intact, retry works; second print = REPRINT + audit; first successful print after a failure is the original.

### Technical Approach
- The printer receives rendered lines + barcode value (content stays configurable in WeighingMS, IR-16).
- Date printed in the station time zone (configuration, default Asia/Dhaka) at completion time.
- Reprint decided by the print log (successful prints only).

### Acceptance Criteria
- [ ] Ticket matches the prototype fields for B-24187
- [ ] Print stores the ticket in the Dummy Printer and returns its ID
- [ ] Printer down → clear error, completion unaffected; retry works
- [ ] Second print marked REPRINT and audited
- [ ] `npm run check` green

### Checkpoint — plan review (delegated, self-validated)
Covers all three stories; printer behind a port; content configurable; testable against the dummy printer. **APPROVE PLAN.**
