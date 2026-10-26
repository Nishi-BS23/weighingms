"""Scanner and printer adapters (training: Dummy Scanner / Dummy Printer)."""

import logging

import httpx

from weighingms.application.ports import (
    PrinterUnavailable,
    PrintReceipt,
    ScanEvent,
    ScannerUnavailable,
)
from weighingms.domain.errors import DependencyUnavailable
from weighingms.infrastructure.devices.contract import WirePrintReceipt, WireScanBatch
from weighingms.infrastructure.devices.http import call, parse

log = logging.getLogger("weighingms.devices")

_SCANNER_MESSAGE = "The barcode scanner is not available. Touch a row to select a batch."


class HttpScannerAdapter:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def scans_after(self, seq: int) -> tuple[list[ScanEvent], int]:
        batch = self._fetch(seq)
        if batch.last_seq < seq:
            # The scanner restarted (training reset): its sequence began again at 1.
            batch = self._fetch(0)
        scans = [ScanEvent(seq=s.seq, code=s.code, scanned_at=s.scanned_at) for s in batch.scans]
        return scans, batch.last_seq

    def is_available(self) -> bool:
        return _available(self._client, "/api/scanner/status")

    def _fetch(self, seq: int) -> WireScanBatch:
        response = call(
            self._client,
            "GET",
            "/api/scanner/scans",
            ScannerUnavailable,
            _SCANNER_MESSAGE,
            params={"after": seq},
        )
        return parse(WireScanBatch, response, ScannerUnavailable, _SCANNER_MESSAGE)


_PRINTER_MESSAGE = "Printer not available. Check the printer and try again."


class HttpPrinterAdapter:
    """Ticket printer (training: Dummy Printer `POST /api/tickets`)."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def is_available(self) -> bool:
        return _available(self._client, "/api/printer/status")

    def print_ticket(
        self, batch_id: str, session_id: str, lines: list[str], barcode_value: str, reprint: bool
    ) -> PrintReceipt:
        body = {
            "batchId": batch_id,
            "sessionId": session_id,
            "reprint": reprint,
            "lines": lines,
            "barcodeValue": barcode_value,
        }
        try:
            response = call(
                self._client,
                "POST",
                "/api/tickets",
                PrinterUnavailable,
                _PRINTER_MESSAGE,
                json=body,
            )
        except PrinterUnavailable:
            log.warning("Printing the ticket for %s failed", batch_id)
            raise
        receipt = parse(WirePrintReceipt, response, PrinterUnavailable, _PRINTER_MESSAGE)
        return PrintReceipt(ticket_id=receipt.ticket_id, printed_at=receipt.printed_at)


def _available(client: httpx.Client, path: str) -> bool:
    try:
        call(client, "GET", path, DependencyUnavailable, "unavailable")
    except DependencyUnavailable:
        return False
    return True
