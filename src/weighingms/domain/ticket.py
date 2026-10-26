"""The weighing ticket that travels with the container (FR-18, BR-15; prototype ticket)."""

from dataclasses import dataclass

from weighingms.domain.quantity import Quantity

NAME_WIDTH = 12
NUMBER_WIDTH = 7
RULE = "-" * 32


@dataclass(frozen=True)
class TicketLine:
    short_name: str
    target: Quantity
    actual: Quantity
    overridden: bool


@dataclass(frozen=True)
class Ticket:
    header: str
    batch_id: str
    order_ref: str
    machine_ref: str
    shade_code: str
    date: str
    """Local completion time, "YYYY-MM-DD HH:MM"."""
    operator_name: str
    lines: tuple[TicketLine, ...]
    reprint: bool

    @property
    def overridden_count(self) -> int:
        return sum(1 for line in self.lines if line.overridden)

    @property
    def result_line(self) -> str:
        if self.overridden_count == 0:
            return "ALL WITHIN TOLERANCE"
        return f"{self.overridden_count} OVERRIDDEN (*)"

    @property
    def barcode_value(self) -> str:
        return self.batch_id

    def text_lines(self) -> list[str]:
        """The ticket as printed: fixed-width text lines; the printer renders the barcode."""
        rows = [self.header]
        if self.reprint:
            rows.append("*** REPRINT ***")
        rows += [
            RULE,
            f"BATCH   {self.batch_id}",
            f"ORDER   {self.order_ref}",
            f"MACHINE {self.machine_ref}",
            f"SHADE   {self.shade_code}",
            f"DATE    {self.date}",
            f"OPER.   {self.operator_name}",
            RULE,
            f"{'COMPONENT':<{NAME_WIDTH}}{'TGT':>{NUMBER_WIDTH}}{'ACT':>{NUMBER_WIDTH}}",
        ]
        for line in self.lines:
            name = (line.short_name + ("*" if line.overridden else ""))[:NAME_WIDTH]
            rows.append(
                f"{name:<{NAME_WIDTH}}{line.target.display():>{NUMBER_WIDTH}}"
                f"{line.actual.to(line.target.unit).display():>{NUMBER_WIDTH}} {line.target.unit}"
            )
        rows += [RULE, self.result_line, f"[BARCODE {self.barcode_value}]", self.batch_id]
        return rows
