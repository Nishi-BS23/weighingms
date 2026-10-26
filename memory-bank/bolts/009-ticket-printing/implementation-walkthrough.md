---
stage: implement
bolt: 009-ticket-printing
created: 2026-10-26T09:08:23Z
---

## Implementation Walkthrough: 005-ticket-printing

### Summary

A completed session can now produce its weighing ticket — the prototype's content and layout — as structured data for the preview and as text lines for the printer. Printing goes through a printer port to the Dummy Printer, every successful print is logged, and any print after the first is marked REPRINT and audited.

### Structure Overview

The ticket model and its fixed-width rendering live in the domain; the ticket service composes it from the session snapshot, the records and the operator directory, decides original vs reprint from the print log, and calls the printer port. The printer adapter extends the earlier printer probe, so device status and printing share one adapter. Header text and the station time zone come from configuration.

### Completed Work

- [x] `config/station.toml` - `[ticket] header`, `[station] timezone = "Asia/Dhaka"`
- [x] `src/weighingms/config.py` - ticket header and time zone
- [x] `src/weighingms/domain/ticket.py` - ticket, lines, result line, barcode value, text rendering
- [x] `src/weighingms/application/ports.py` - `PrinterPort`, `PrintReceipt`, `PrinterUnavailable`, `PrintStore`
- [x] `src/weighingms/application/tickets.py` - preview, print, reprint + audit
- [x] `src/weighingms/infrastructure/devices/peripherals_adapter.py`, `contract.py` - `HttpPrinterAdapter` (print + availability)
- [x] `src/weighingms/infrastructure/persistence/migrations/versions/0003_print_log.py`, `tables.py`, `repositories.py` - print log
- [x] `src/weighingms/api/tickets.py` - `GET /api/sessions/{id}/ticket`, `POST /api/sessions/{id}/ticket/print`
- [x] `src/weighingms/api/container.py`, `api/app.py` - wiring; training reset clears the print log

### Key Decisions

- **Printer receives rendered lines**: content (header, fields, short names) changes in configuration without touching the printer integration (IR-16).
- **Reprint = any successful print after the first**: a failed print does not count, so the first successful print is always the original.
- **Date in station time**: completion time shown in the configured time zone, as an operator reads a wall clock.

### Deviations from Plan

None.

### Dependencies Added

None.

### Developer Notes

Smoke run: ticket text equals the prototype layout for the prototype actuals; print 1 original, print 2 "*** REPRINT ***"; dummy printer holds both; printer down → 503 `PRINTER_UNAVAILABLE` with plain message.

### Stage checkpoint (delegated, self-validated)

Deliverables complete; lint and types clean; existing tests green. **Approved** — proceed to Test.
