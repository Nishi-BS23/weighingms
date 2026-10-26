"""Tolerance evaluation of the live net weight (FR-10 – FR-12, FR-14 detection)."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from weighingms.domain.quantity import Quantity
from weighingms.domain.tolerance import ToleranceBand

NEAR_FRACTION = Decimal("0.9")
"""Below the band but at least 90% of target: amber visual cue (prototype `zone()`, TA-05)."""


class WeighingZone(StrEnum):
    UNDER = "UNDER"
    NEAR = "NEAR"
    WITHIN = "WITHIN"
    OVER = "OVER"
    OFFLINE = "OFFLINE"


class Action(StrEnum):
    CONFIRM = "CONFIRM"
    RETARE = "RETARE"
    QUIT = "QUIT"
    OVERRIDE = "OVERRIDE"


@dataclass(frozen=True)
class Evaluation:
    zone: WeighingZone
    net: Quantity | None
    """Net weight at the component's display precision, or None when no trustworthy reading."""
    remaining: Quantity
    surplus: Quantity | None
    surplus_pct: Decimal | None
    can_confirm: bool
    scale_available: bool
    calibration_valid: bool
    stable: bool
    status_text: str
    allowed_actions: tuple[Action, ...]
    guidance: str | None = None
    """How to recover from an over-dose (Step 24 decision, ADR-004)."""


def evaluate(
    band: ToleranceBand,
    net: Quantity | None,
    *,
    calibration_valid: bool = True,
    stable: bool = True,
) -> Evaluation:
    """Classify a net weight against an inclusive tolerance band.

    The net weight is first rounded to the component's display precision so that the rule and the
    number the operator sees always agree (e.g. 93.5 g shown means 93.5 g evaluated).
    """
    target = band.target
    unit = target.unit
    if net is None:
        return Evaluation(
            zone=WeighingZone.OFFLINE,
            net=None,
            remaining=target.rounded(),
            surplus=None,
            surplus_pct=None,
            can_confirm=False,
            scale_available=False,
            calibration_valid=calibration_valid,
            stable=False,
            status_text="SCALE OFFLINE — CHECK CONNECTION",
            allowed_actions=(Action.QUIT,),
        )

    shown = net.to(unit).rounded()
    remaining = max(target - shown, Quantity(Decimal(0), unit), key=lambda q: q.value).rounded()
    surplus: Quantity | None = None
    surplus_pct: Decimal | None = None

    if shown > band.maximum:
        zone = WeighingZone.OVER
        surplus = (shown - target).rounded()
        surplus_pct = (surplus.value / target.value * 100).quantize(Decimal("0.1"), ROUND_HALF_UP)
    elif shown >= band.minimum:
        zone = WeighingZone.WITHIN
    elif shown.value >= target.value * NEAR_FRACTION:
        zone = WeighingZone.NEAR
    else:
        zone = WeighingZone.UNDER

    can_confirm = zone is WeighingZone.WITHIN and calibration_valid
    actions = [Action.RETARE, Action.QUIT]
    if can_confirm:
        actions.insert(0, Action.CONFIRM)
    if zone is not WeighingZone.WITHIN and shown.value > 0:
        actions.append(Action.OVERRIDE)

    if not calibration_valid:
        text = "SCALE CALIBRATION EXPIRED — CALL SUPERVISOR"
    elif zone is WeighingZone.WITHIN:
        text = "WITHIN TOLERANCE — PRESS OK TO CONFIRM"
    elif zone is WeighingZone.OVER and surplus is not None:
        text = f"OVER TOLERANCE — SURPLUS +{surplus.display()} {unit}"
    else:
        text = f"DISPENSE — {remaining.display()} {unit} REMAINING"

    guidance = None
    if zone is WeighingZone.OVER:
        guidance = (
            f"Remove material until the weight is back within {band.minimum.display()} – "
            f"{band.maximum.display()} {unit}, or empty the container and press Re-tare to weigh "
            "again. A supervisor can authorise accepting the over-dose."
        )

    return Evaluation(
        zone=zone,
        net=shown,
        remaining=remaining,
        surplus=surplus,
        surplus_pct=surplus_pct,
        can_confirm=can_confirm,
        scale_available=True,
        calibration_valid=calibration_valid,
        stable=stable,
        status_text=text,
        allowed_actions=tuple(actions),
        guidance=guidance,
    )


def display_max(band: ToleranceBand) -> Quantity:
    """Progress-bar full scale: about 4/3 of target, rounded to a tidy value (display only)."""
    raw = band.target.value * 4 / 3
    step = Decimal(5).scaleb(raw.adjusted() - 2)
    value = (raw / step).to_integral_value(ROUND_HALF_UP) * step
    minimum = band.maximum.value * Decimal("1.1")
    if value < minimum:
        value = (minimum / step).to_integral_value(ROUND_HALF_UP) * step + step
    return Quantity(value, band.target.unit).rounded()
