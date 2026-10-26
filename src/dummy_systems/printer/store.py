"""Dummy Printer: tickets are 'printed' by storing them (SQLite), so they can be inspected."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import Field
from sqlalchemy import Engine, String, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from dummy_systems.common.models import ApiModel


class TicketRequest(ApiModel):
    batch_id: str
    session_id: str | None = None
    reprint: bool = False
    lines: list[str] = Field(min_length=1)
    """Rendered text lines, top to bottom (the printer does not compose content)."""
    barcode_value: str = Field(min_length=1)


class PrintReceipt(ApiModel):
    ticket_id: str
    status: Literal["PRINTED"]
    printed_at: datetime


class PrintedTicket(TicketRequest):
    ticket_id: str
    printed_at: datetime


class _Base(DeclarativeBase):
    pass


class _TicketRow(_Base):
    __tablename__ = "printer_tickets"

    ticket_id: Mapped[str] = mapped_column(String, primary_key=True)
    printed_at: Mapped[str] = mapped_column(String)
    payload: Mapped[str] = mapped_column(Text)


class PrinterStore:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        _Base.metadata.create_all(engine)

    def print(self, request: TicketRequest, at: datetime) -> PrintReceipt:
        ticket_id = f"TKT-{uuid.uuid4().hex[:10].upper()}"
        with Session(self._engine) as session, session.begin():
            session.add(
                _TicketRow(
                    ticket_id=ticket_id,
                    printed_at=at.isoformat(),
                    payload=request.model_dump_json(by_alias=True),
                )
            )
        return PrintReceipt(ticket_id=ticket_id, status="PRINTED", printed_at=at)

    def tickets(self) -> list[PrintedTicket]:
        with Session(self._engine) as session:
            rows = session.scalars(select(_TicketRow).order_by(_TicketRow.printed_at)).all()
            return [self._to_ticket(row) for row in rows]

    def ticket(self, ticket_id: str) -> PrintedTicket | None:
        with Session(self._engine) as session:
            row = session.get(_TicketRow, ticket_id)
            return None if row is None else self._to_ticket(row)

    def reset(self) -> None:
        with Session(self._engine) as session, session.begin():
            session.query(_TicketRow).delete()

    @staticmethod
    def _to_ticket(row: _TicketRow) -> PrintedTicket:
        request = TicketRequest.model_validate_json(row.payload)
        return PrintedTicket(
            **request.model_dump(),
            ticket_id=row.ticket_id,
            printed_at=datetime.fromisoformat(row.printed_at),
        )
