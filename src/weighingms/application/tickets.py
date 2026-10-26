"""Weighing ticket: preview and print (FR-18). Reprints are marked and audited."""

import logging
from dataclasses import dataclass
from datetime import datetime

from weighingms.application.operators import OperatorService
from weighingms.application.ports import (
    AuditStore,
    PrinterPort,
    PrintStore,
    RecordStore,
    SessionStore,
)
from weighingms.clock import Clock, utc_now
from weighingms.config import StationConfig
from weighingms.domain.errors import SessionNotCompleted
from weighingms.domain.ticket import Ticket, TicketLine
from weighingms.domain.weighing.session import SessionStatus, WeighingSession

log = logging.getLogger("weighingms.tickets")


@dataclass(frozen=True)
class PrintResult:
    ticket_id: str
    printed_at: datetime
    reprint: bool
    ticket: Ticket


class TicketService:
    def __init__(
        self,
        sessions: SessionStore,
        records: RecordStore,
        prints: PrintStore,
        printer: PrinterPort,
        operators: OperatorService,
        audit: AuditStore,
        station: StationConfig,
        clock: Clock = utc_now,
    ) -> None:
        self._sessions = sessions
        self._records = records
        self._prints = prints
        self._printer = printer
        self._operators = operators
        self._audit = audit
        self._station = station
        self._clock = clock

    def preview(self, session_id: str) -> Ticket:
        """The ticket the next print would produce (REPRINT once an original has printed)."""
        session = self._completed(session_id)
        return self._compose(session, reprint=self._prints.count_for_session(session_id) > 0)

    def print(self, session_id: str) -> PrintResult:
        ticket = self.preview(session_id)
        receipt = self._printer.print_ticket(
            batch_id=ticket.batch_id,
            session_id=session_id,
            lines=ticket.text_lines(),
            barcode_value=ticket.barcode_value,
            reprint=ticket.reprint,
        )
        operator_id = self._operators.current().operator_id
        now = self._clock()
        self._prints.add(session_id, receipt.ticket_id, ticket.reprint, operator_id, now)
        if ticket.reprint:
            self._audit.add(
                "REPRINT",
                operator_id,
                now,
                session_id=session_id,
                detail={"ticketId": receipt.ticket_id},
            )
        log.info(
            "Ticket %s printed for %s%s",
            receipt.ticket_id,
            ticket.batch_id,
            " (reprint)" if ticket.reprint else "",
        )
        return PrintResult(receipt.ticket_id, receipt.printed_at, ticket.reprint, ticket)

    def _completed(self, session_id: str) -> WeighingSession:
        session = self._sessions.get(session_id)
        if session.status is not SessionStatus.COMPLETED:
            raise SessionNotCompleted(
                f"Batch {session.batch_id} is not completed yet; the ticket is printed at the end."
            )
        return session

    def _compose(self, session: WeighingSession, reprint: bool) -> Ticket:
        records = {r.component_id: r for r in self._records.for_session(session.session_id)}
        lines = []
        for spec in sorted(session.recipe.components, key=lambda s: s.sequence):
            record = records[spec.component_id]
            lines.append(
                TicketLine(
                    short_name=spec.short_name,
                    target=spec.target,
                    actual=record.actual,
                    overridden=record.result == "OVERRIDDEN",
                )
            )
        completed = (session.completed_at or self._clock()).astimezone(self._station.timezone)
        recipe = session.recipe
        return Ticket(
            header=self._station.ticket_header,
            batch_id=session.batch_id,
            order_ref=recipe.order_ref,
            machine_ref=recipe.machine_ref,
            shade_code=recipe.shade_code,
            date=completed.strftime("%Y-%m-%d %H:%M"),
            operator_name=self._station.operators.by_id(session.started_by).name,
            lines=tuple(lines),
            reprint=reprint,
        )
