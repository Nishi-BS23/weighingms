"""Completed-batch summary (FR-16, FR-23; prototype Screen 3)."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from weighingms.domain.operators import OperatorDirectory
from weighingms.domain.quantity import Quantity
from weighingms.domain.weighing.records import WeighingRecord
from weighingms.domain.weighing.session import ComponentSpec, WeighingSession


@dataclass(frozen=True)
class ComponentResult:
    spec: ComponentSpec
    record: WeighingRecord | None


@dataclass(frozen=True)
class BatchSummary:
    session: WeighingSession
    results: list[ComponentResult]
    all_within_tolerance: bool
    overridden_count: int
    total_dispensed: Quantity
    elapsed_seconds: int
    operator_name: str

    @property
    def elapsed_text(self) -> str:
        minutes, seconds = divmod(self.elapsed_seconds, 60)
        return f"{minutes} min {seconds} s"


def summarise(
    session: WeighingSession,
    records: list[WeighingRecord],
    operators: OperatorDirectory,
    now: datetime,
) -> BatchSummary:
    by_component = {r.component_id: r for r in records}
    results = [
        ComponentResult(spec=spec, record=by_component.get(spec.component_id))
        for spec in sorted(session.recipe.components, key=lambda s: s.sequence)
    ]
    total = sum((r.actual.to("kg") for r in records), Quantity(Decimal(0), "kg"))
    overridden = sum(1 for r in records if r.result == "OVERRIDDEN")
    end = session.completed_at or now
    return BatchSummary(
        session=session,
        results=results,
        all_within_tolerance=overridden == 0 and len(records) == len(results),
        overridden_count=overridden,
        total_dispensed=total.rounded(),
        elapsed_seconds=int((end - session.started_at).total_seconds()),
        operator_name=operators.by_id(session.started_by).name,
    )
