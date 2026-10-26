---
stage: test
bolt: 009-ticket-printing
created: 2026-10-26T09:09:06Z
---

## Test Report: 005-ticket-printing

### Summary

- **Tests**: 8 new passed; backend 213/213
- **Coverage**: 97.9% (backend total)
- **Static checks**: ruff format/lint and mypy --strict clean

### Test Files

- [x] `tests/unit/weighingms/test_ticket.py` - full ticket text equals the prototype ticket for the prototype actuals; overridden line marked "*" and result "1 OVERRIDDEN (*)"; REPRINT marker; barcode value
- [x] `tests/api/weighingms/test_tickets_api.py` - ticket only for completed batches (409); preview fields incl. local date and short names; print then reprint (dummy printer holds both, REPRINT audit, preview switches to reprint); printer down → 503 with plain message, batch stays completed, retry prints the original; overridden component appears on the ticket
- [x] `tests/integration/weighingms/test_device_adapters.py` - printer adapter availability (renamed adapter)

### Acceptance Criteria Validation

- ✅ **001-compose-weighing-ticket**: header, batch, order, machine, shade, date, operator, component lines, result line, barcode value; only for completed sessions; header and short names from configuration
- ✅ **002-print-ticket**: `POST /api/tickets` to the Dummy Printer, ticket ID returned and logged; printer down → 503 `PRINTER_UNAVAILABLE`, completion intact, retry works (evidence/STEP-27-printer-api.json)
- ✅ **003-reprint-ticket**: second print `reprint: true` with "*** REPRINT ***" and REPRINT audit; failed print does not count

### Issues Found

None.

### Notes

The barcode is sent as a value; the UI preview draws bars from it (bolt 010) and a real label printer would render its own symbology (UQ-11).

### Stage checkpoint (delegated, self-validated)

All tests pass; all acceptance criteria verified. **Approved** — bolt complete.
