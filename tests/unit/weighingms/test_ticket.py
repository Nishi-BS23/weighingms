"""Ticket composition and text layout (story 005/001; prototype ticket)."""

from weighingms.domain.quantity import Quantity
from weighingms.domain.ticket import Ticket, TicketLine


def _line(name: str, target: str, actual: str, unit: str, overridden: bool = False) -> TicketLine:
    return TicketLine(name, Quantity.of(target, unit), Quantity.of(actual, unit), overridden)  # type: ignore[arg-type]


PROTOTYPE_LINES = (
    _line("Blue RSPL", "1240.0", "1241.5", "g"),
    _line("Red RB", "386.0", "385.4", "g"),
    _line("Yellow RGB", "94.0", "94.2", "g"),
    _line("Na2SO4", "24.000", "23.980", "kg"),
    _line("Soda Ash", "9.600", "9.621", "kg"),
)


def _ticket(lines: tuple[TicketLine, ...] = PROTOTYPE_LINES, reprint: bool = False) -> Ticket:
    return Ticket(
        header="FCI DYEING — WEIGHING TICKET",
        batch_id="B-24187",
        order_ref="SO-9931",
        machine_ref="JET-04",
        shade_code="Teal 4C",
        date="2026-08-04 07:48",
        operator_name="R. Karim",
        lines=lines,
        reprint=reprint,
    )


def test_ticket_text_reproduces_the_prototype_ticket() -> None:
    assert _ticket().text_lines() == [
        "FCI DYEING — WEIGHING TICKET",
        "--------------------------------",
        "BATCH   B-24187",
        "ORDER   SO-9931",
        "MACHINE JET-04",
        "SHADE   Teal 4C",
        "DATE    2026-08-04 07:48",
        "OPER.   R. Karim",
        "--------------------------------",
        "COMPONENT       TGT    ACT",
        "Blue RSPL    1240.0 1241.5 g",
        "Red RB        386.0  385.4 g",
        "Yellow RGB     94.0   94.2 g",
        "Na2SO4       24.000 23.980 kg",
        "Soda Ash      9.600  9.621 kg",
        "--------------------------------",
        "ALL WITHIN TOLERANCE",
        "[BARCODE B-24187]",
        "B-24187",
    ]


def test_overridden_component_is_marked_and_counted() -> None:
    lines = (*PROTOTYPE_LINES[:2], _line("Yellow RGB", "94.0", "96.4", "g", overridden=True))
    ticket = _ticket(lines)

    assert ticket.result_line == "1 OVERRIDDEN (*)"
    assert "Yellow RGB*    94.0   96.4 g" in ticket.text_lines()


def test_reprint_is_marked_under_the_header() -> None:
    assert _ticket(reprint=True).text_lines()[1] == "*** REPRINT ***"
    assert _ticket().barcode_value == "B-24187"
