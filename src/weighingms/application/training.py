"""Training simulation for the component being weighed (training build only, ADR-003)."""

from decimal import Decimal
from typing import Literal

from weighingms.application.ports import TrainingControlPort
from weighingms.application.sessions import SessionService
from weighingms.domain.quantity import Quantity

SimulationKind = Literal["dispense", "overshoot", "below"]

_LANDING_TOLERANCE_FACTOR: dict[SimulationKind, Decimal] = {
    "dispense": Decimal("0.4"),
    "overshoot": Decimal("4.8"),
}
_BELOW_FRACTION = Decimal("0.8")


class TrainingService:
    def __init__(self, sessions: SessionService, control: TrainingControlPort) -> None:
        self._sessions = sessions
        self._control = control

    def simulate(self, session_id: str, kind: SimulationKind) -> Quantity:
        """Pour onto the active component's scale; returns the landing net weight.

        Landing values reproduce the prototype's buttons (ui-analysis R15): dispense lands at
        target + 0.4 × tolerance, overshoot at target + 4.8 × tolerance, below at 80% of target.
        """
        spec = self._sessions.live(session_id).spec
        target, tol = spec.band.target, spec.band.plus_minus.to(spec.band.target.unit)
        if kind == "below":
            landing = Quantity(target.value * _BELOW_FRACTION, target.unit).rounded()
        else:
            landing = target + Quantity(tol.value * _LANDING_TOLERANCE_FACTOR[kind], target.unit)
            landing = landing.rounded()
        self._control.simulate(spec.scale.scale_id, kind, landing)
        return landing

    def reset_weighing(self, session_id: str) -> None:
        """The prototype's Reset: take the material off the scale (net back to zero)."""
        spec = self._sessions.live(session_id).spec
        self._control.simulate(spec.scale.scale_id, "exact", Quantity(Decimal(0), spec.target.unit))
