"""Simulated pour: how a person dispenses — fast at first, easing as the landing value nears.

Reproduces the prototype's behaviour (ui-analysis R14): every 34 ms the net weight moves by
max(0.4% of the landing value, 5.5% of the remaining distance) until it reaches the landing value.
Computed lazily from elapsed time, so no background thread is needed and tests can drive time.
"""

from dataclasses import dataclass
from decimal import Decimal

TICK_SECONDS = 0.034
_MIN_STEP_FRACTION = Decimal("0.004")
_REMAINING_FRACTION = Decimal("0.055")
_MAX_TICKS = 5000


@dataclass(frozen=True)
class Ramp:
    start_net: Decimal
    landing_net: Decimal
    started_at: float
    min_step: Decimal
    """Absolute floor for a step (the scale resolution), so a ramp always terminates."""


def net_at(ramp: Ramp, now: float) -> tuple[Decimal, bool]:
    """Return (net weight, settled) for the ramp at monotonic time `now`."""
    ticks = min(int(max(0.0, now - ramp.started_at) / TICK_SECONDS), _MAX_TICKS)
    distance = abs(ramp.landing_net - ramp.start_net)
    direction = 1 if ramp.landing_net >= ramp.start_net else -1
    min_step = max(abs(ramp.landing_net) * _MIN_STEP_FRACTION, ramp.min_step)
    moved = Decimal(0)
    for _ in range(ticks):
        remaining = distance - moved
        if remaining <= ramp.min_step / 10:
            return ramp.landing_net, True
        moved = min(distance, moved + max(min_step, remaining * _REMAINING_FRACTION))
    if moved >= distance:
        return ramp.landing_net, True
    return ramp.start_net + direction * moved, False
