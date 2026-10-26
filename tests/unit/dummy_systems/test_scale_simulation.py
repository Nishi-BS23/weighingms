"""Eased ramp: the simulated pour of the prototype (ui-analysis R14)."""

from decimal import Decimal

from dummy_systems.scale.simulation import TICK_SECONDS, Ramp, net_at


def _ramp(start: str, landing: str, resolution: str = "0.1") -> Ramp:
    return Ramp(
        start_net=Decimal(start),
        landing_net=Decimal(landing),
        started_at=0.0,
        min_step=Decimal(resolution),
    )


def test_ramp_starts_at_its_start_value() -> None:
    assert net_at(_ramp("0", "94.2"), 0.0) == (Decimal(0), False)


def test_ramp_rises_monotonically_and_eases() -> None:
    ramp = _ramp("0", "94.2")
    values = [net_at(ramp, i * TICK_SECONDS)[0] for i in range(0, 40)]
    steps = [b - a for a, b in zip(values, values[1:], strict=False)]

    assert all(step >= 0 for step in steps)
    assert steps[0] > steps[20]  # fast first, slower near the landing value


def test_ramp_settles_exactly_on_the_landing_value() -> None:
    net, settled = net_at(_ramp("0", "94.2"), 60.0)

    assert (net, settled) == (Decimal("94.2"), True)


def test_ramp_can_move_downwards() -> None:
    ramp = _ramp("96.4", "94.0")

    mid, settled_mid = net_at(ramp, 3 * TICK_SECONDS)
    end, settled_end = net_at(ramp, 60.0)

    assert Decimal("94.0") < mid < Decimal("96.4") and not settled_mid
    assert (end, settled_end) == (Decimal("94.0"), True)


def test_ramp_to_zero_terminates() -> None:
    assert net_at(_ramp("5.0", "0"), 60.0) == (Decimal(0), True)
