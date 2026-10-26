"""Dummy Printer endpoints — training contract (Workbook minimum: POST /api/tickets)."""

from fastapi import APIRouter, Depends

from dummy_systems.common.clock import Clock
from dummy_systems.common.errors import ApiError
from dummy_systems.common.models import DeviceStatus
from dummy_systems.control.availability import Availability
from dummy_systems.printer.store import PrintedTicket, PrinterStore, PrintReceipt, TicketRequest


def build_router(store: PrinterStore, availability: Availability, clock: Clock) -> APIRouter:
    router = APIRouter(
        tags=["Dummy Printer (training contract)"],
        dependencies=[Depends(availability.dependency("printer"))],
    )

    @router.post("/api/tickets", response_model=PrintReceipt)
    def print_ticket(request: TicketRequest) -> PrintReceipt:
        return store.print(request, clock())

    @router.get("/api/tickets", response_model=list[PrintedTicket])
    def list_tickets() -> list[PrintedTicket]:
        return store.tickets()

    @router.get("/api/tickets/{ticket_id}", response_model=PrintedTicket)
    def get_ticket(ticket_id: str) -> PrintedTicket:
        ticket = store.ticket(ticket_id)
        if ticket is None:
            raise ApiError(404, "TICKET_NOT_FOUND", f"Ticket {ticket_id} does not exist.")
        return ticket

    @router.get("/api/printer/status", response_model=DeviceStatus)
    def status() -> DeviceStatus:
        return DeviceStatus(available=True)

    return router
