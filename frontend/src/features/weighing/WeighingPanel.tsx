import type { ActiveContext, Live, SessionComponent } from "../../api/types";
import { barGeometry } from "./bar-geometry";

interface PanelProps {
  component: SessionComponent;
  active: ActiveContext;
  /** Live evaluation for this component; undefined until the first reading arrives. */
  live: Live | undefined;
  overrideRequested: boolean;
}

/** Weigh header (identity, lot, container, tare) and scale badge (FR-4 – FR-8). */
export function WeighHeader({ component, active }: Pick<PanelProps, "component" | "active">) {
  return (
    <div className="weigh-head">
      <div className="who">
        <span className="nm">{component.name}</span>
        <span className="meta">
          {component.dyestuffCode} · LOT {component.lotId} · CONTAINER {active.containerId} · TARE{" "}
          {active.tare.value} {active.tare.unit}
        </span>
      </div>
      <div className="scale-badge">
        <span className="k">Scale selected</span>
        <span className="v" data-testid="scale-selected">
          {component.scale.label}
        </span>
        <span className="auto">automatic</span>
      </div>
    </div>
  );
}

/** Weighed now / Still to weigh / Target (FR-9 – FR-11). Values come from the API. */
export function Readout({ component, live }: Pick<PanelProps, "component" | "live">) {
  const unit = component.target.unit;
  const zone = live?.zone ?? "UNDER";
  return (
    <div className="readout">
      <div className="cell live" data-zone={zone}>
        <span className="k">Weighed now</span>
        <span className="v">
          <span data-testid="weighed-now">{live?.net ? live.net.value : "—"}</span>{" "}
          <span className="u">{unit}</span>
        </span>
      </div>
      <div className="cell">
        <span className="k">Still to weigh</span>
        <span className="v">
          <span data-testid="still-to-weigh">
            {live ? live.remaining.value : component.target.value}
          </span>{" "}
          <span className="u">{unit}</span>
        </span>
      </div>
      <div className="cell">
        <span className="k">Target</span>
        <span className="v">
          {component.target.value} <span className="u">{unit}</span>
        </span>
      </div>
    </div>
  );
}

/** Progress bar with tolerance band and target line, caption and status line (FR-12). */
export function ToleranceBar({ component, active, live, overrideRequested }: PanelProps) {
  const { tolerance, target } = component;
  const unit = target.unit;
  const zone = live?.zone ?? "UNDER";
  const g = barGeometry(
    live?.net?.value ?? null,
    tolerance.minimum.value,
    tolerance.maximum.value,
    target.value,
    active.displayMax.value,
  );
  const statusText = overrideRequested
    ? "OVERRIDE REQUESTED — AWAITING SUPERVISOR"
    : (live?.statusText ?? `DISPENSE — ${target.value} ${unit} REMAINING`);
  return (
    <div className="bar-block">
      <div
        className="bar"
        data-zone={zone}
        role="progressbar"
        aria-label="Weighing progress"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(g.fillPct)}
      >
        <div className="fill" style={{ width: `${g.fillPct}%` }} />
        <div className="band" style={{ left: `${g.bandLeftPct}%`, width: `${g.bandWidthPct}%` }} />
        <div className="target-line" style={{ left: `${g.targetPct}%` }} />
      </div>
      <div className="bar-caption">
        <span>0</span>
        <span data-testid="tolerance-caption">
          TOLERANCE ±{tolerance.plusMinus.value} {unit}&nbsp; ({tolerance.minimum.value} –{" "}
          {tolerance.maximum.value})
        </span>
        <span>
          {active.displayMax.value} {unit}
        </span>
      </div>
      <div className="status-line" data-zone={zone} data-testid="status-line" role="status">
        {statusText}
      </div>
    </div>
  );
}

/** Over-dose panel with the Step 24 recovery guidance (FR-14, ADR-004). */
export function SurplusPanel({ live, unit }: { live: Live | undefined; unit: string }) {
  if (live?.zone !== "OVER" || !live.surplus) return null;
  return (
    <div className="surplus" role="alert">
      <span className="h">
        Surplus +{live.surplus.value} {unit} (+{live.surplusPct}%) — over tolerance
      </span>
      {live.guidance && <span className="g">{live.guidance}</span>}
    </div>
  );
}
