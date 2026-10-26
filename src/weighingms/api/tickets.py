"""Weighing ticket endpoints used by Screen 3 (FR-18)."""

from datetime import datetime

from fastapi import APIRouter, Depends

from weighingms.api.container import Container, get_container
from weighingms.api.schemas import ApiModel, QuantityOut
from weighingms.domain.ticket import Ticket

router = APIRouter(prefix="/api/sessions", tags=["Tickets"])


class TicketLineOut(ApiModel):
    short_name: str
    target: QuantityOut
    actual: QuantityOut
    overridden: bool


class TicketOut(ApiModel):
    header: str
    batch_id: str
    order_ref: str
    machine_ref: str
    shade_code: str
    date: str
    operator_name: str
    lines: list[TicketLineOut]
    result_line: str
    barcode_value: str
    reprint: bool
    text: list[str]

    @classmethod
    def of(cls, t: Ticket) -> "TicketOut":
        return cls(
            header=t.header,
            batch_id=t.batch_id,
            order_ref=t.order_ref,
            machine_ref=t.machine_ref,
            shade_code=t.shade_code,
            date=t.date,
            operator_name=t.operator_name,
            lines=[
                TicketLineOut(
                    short_name=line.short_name,
                    target=QuantityOut.of(line.target),
                    actual=QuantityOut.of(line.actual.to(line.target.unit)),
                    overridden=line.overridden,
                )
                for line in t.lines
            ],
            result_line=t.result_line,
            barcode_value=t.barcode_value,
            reprint=t.reprint,
            text=t.text_lines(),
        )


class PrintOut(ApiModel):
    ticket_id: str
    printed_at: datetime
    reprint: bool
    ticket: TicketOut


@router.get("/{session_id}/ticket", response_model=TicketOut)
def preview(session_id: str, container: Container = Depends(get_container)) -> TicketOut:
    return TicketOut.of(container.tickets.preview(session_id))


@router.post("/{session_id}/ticket/print", response_model=PrintOut)
def print_ticket(session_id: str, container: Container = Depends(get_container)) -> PrintOut:
    result = container.tickets.print(session_id)
    return PrintOut(
        ticket_id=result.ticket_id,
        printed_at=result.printed_at,
        reprint=result.reprint,
        ticket=TicketOut.of(result.ticket),
    )
