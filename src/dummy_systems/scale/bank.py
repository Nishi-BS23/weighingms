"""State of the two simulated scales (thread-safe)."""

import threading
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from dummy_systems.common.clock import Clock, Ticker
from dummy_systems.common.errors import ApiError
from dummy_systems.common.models import Quantity, Unit
from dummy_systems.scale.models import ScaleClass, ScaleReading, SimulationProfile
from dummy_systems.scale.simulation import Ramp, net_at

CALIBRATION_VALIDITY = timedelta(days=180)


@dataclass(frozen=True)
class ScaleSpec:
    scale_id: str
    scale_class: ScaleClass
    label: str
    unit: Unit
    """Native display unit of the indicator."""
    capacity: Decimal
    """Capacity in the native unit."""
    capacity_kg: Decimal
    resolution: Decimal


SCALES = (
    ScaleSpec(
        "scale-3kg",
        "PRECISION",
        "3 kg precision",
        "g",
        Decimal("3000.0"),
        Decimal(3),
        Decimal("0.1"),
    ),
    ScaleSpec(
        "scale-32kg", "FLOOR", "32 kg floor", "kg", Decimal("32.000"), Decimal(32), Decimal("0.001")
    ),
)


def to_unit(quantity: Quantity, unit: Unit) -> Decimal:
    if quantity.unit == unit:
        return quantity.value
    if quantity.unit == "g":
        return quantity.value / 1000
    return quantity.value * 1000


@dataclass
class _ScaleState:
    spec: ScaleSpec
    calibration_due: date
    gross: Decimal = Decimal(0)
    tare: Decimal = Decimal(0)
    ramp: Ramp | None = field(default=None)


class ScaleBank:
    def __init__(self, clock: Clock, ticker: Ticker, specs: tuple[ScaleSpec, ...] = SCALES) -> None:
        self._clock = clock
        self._ticker = ticker
        self._specs = specs
        self._lock = threading.Lock()
        self._state: dict[str, _ScaleState] = {}
        self.reset()

    def reset(self) -> None:
        due = self._clock().date() + CALIBRATION_VALIDITY
        with self._lock:
            self._state = {
                s.scale_id: _ScaleState(spec=s, calibration_due=due) for s in self._specs
            }

    def specs(self) -> list[ScaleSpec]:
        return list(self._specs)

    def calibration_due(self, scale_id: str) -> date:
        return self._get(scale_id).calibration_due

    def calibration_valid(self, scale_id: str) -> bool:
        return self._clock().date() <= self.calibration_due(scale_id)

    def simulating(self, scale_id: str) -> bool:
        with self._lock:
            state = self._get(scale_id)
            self._settle(state)
            return state.ramp is not None

    def reading(self, scale_id: str) -> ScaleReading:
        with self._lock:
            state = self._get(scale_id)
            net, settled = self._current_net(state)
            return self._reading(state, net, settled)

    def tare(self, scale_id: str) -> ScaleReading:
        """Zero the net weight. A running ramp continues relative to the new tare."""
        with self._lock:
            state = self._get(scale_id)
            net, _ = self._current_net(state)
            state.tare = state.tare + net
            state.gross = state.tare
            if state.ramp is not None:
                state.ramp = Ramp(
                    start_net=Decimal(0),
                    landing_net=state.ramp.landing_net - net,
                    started_at=self._ticker(),
                    min_step=state.spec.resolution,
                )
            return self._reading(state, Decimal(0), state.ramp is None)

    def simulate(self, scale_id: str, profile: SimulationProfile, net: Quantity) -> None:
        with self._lock:
            state = self._get(scale_id)
            target = to_unit(net, state.spec.unit)
            if target < 0:
                raise ApiError(422, "INVALID_WEIGHT", "Net weight cannot be negative.")
            current, _ = self._current_net(state)
            state.gross = state.tare + current
            if profile == "exact":
                state.ramp = None
                state.gross = state.tare + target
            else:
                state.ramp = Ramp(
                    start_net=current,
                    landing_net=target,
                    started_at=self._ticker(),
                    min_step=state.spec.resolution,
                )

    def place(self, scale_id: str, gross: Quantity) -> None:
        """Replace whatever is on the scale with `gross` (e.g. a new empty container)."""
        with self._lock:
            state = self._get(scale_id)
            value = to_unit(gross, state.spec.unit)
            if value < 0:
                raise ApiError(422, "INVALID_WEIGHT", "A load cannot be negative.")
            state.ramp = None
            state.gross = value

    def set_calibration(self, scale_id: str, due: date) -> None:
        with self._lock:
            self._get(scale_id).calibration_due = due

    def _get(self, scale_id: str) -> _ScaleState:
        state = self._state.get(scale_id)
        if state is None:
            raise ApiError(404, "SCALE_NOT_FOUND", f"Scale {scale_id} does not exist.")
        return state

    def _settle(self, state: _ScaleState) -> None:
        if state.ramp is not None:
            net, settled = net_at(state.ramp, self._ticker())
            if settled:
                state.gross = state.tare + net
                state.ramp = None

    def _current_net(self, state: _ScaleState) -> tuple[Decimal, bool]:
        if state.ramp is None:
            return state.gross - state.tare, True
        net, settled = net_at(state.ramp, self._ticker())
        if settled:
            state.gross = state.tare + net
            state.ramp = None
        return net, settled

    def _reading(self, state: _ScaleState, net: Decimal, stable: bool) -> ScaleReading:
        spec = state.spec
        gross = min(state.tare + net, spec.capacity)
        gross = max(gross, Decimal(0))
        clamped_net = gross - state.tare
        return ScaleReading(
            scale_id=spec.scale_id,
            gross=_quantity(gross, spec),
            tare=_quantity(state.tare, spec),
            net=_quantity(clamped_net, spec),
            stable=stable,
            read_at=self._clock(),
        )


def _quantity(value: Decimal, spec: ScaleSpec) -> Quantity:
    """Round a raw value to the indicator's resolution, as a real indicator displays it."""
    return Quantity(value=value.quantize(spec.resolution, rounding=ROUND_HALF_UP), unit=spec.unit)
