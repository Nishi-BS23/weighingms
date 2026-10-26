import { useState } from "react";
import { api } from "../../api/client";
import { plainMessage } from "../../shared/messages";
import { useResource } from "../../shared/use-resource";
import type { SimulationKind } from "../../api/types";

const SYSTEMS: { id: string; label: string }[] = [
  { id: "orgatex", label: "OrgaTEX" },
  { id: "scale-3kg", label: "Scale 3 kg" },
  { id: "scale-32kg", label: "Scale 32 kg" },
  { id: "scanner", label: "Scanner" },
  { id: "printer", label: "Printer" },
];

function useAction(): [string | null, (action: () => Promise<unknown>) => Promise<void>] {
  const [note, setNote] = useState<string | null>(null);
  const run = async (action: () => Promise<unknown>) => {
    setNote(null);
    try {
      await action();
    } catch (e) {
      setNote(plainMessage(e));
    }
  };
  return [note, run];
}

interface SimulationProps {
  /** Simulation of the active component; undefined while no component is being weighed. */
  onSimulate?: (kind: SimulationKind) => Promise<void>;
  onResetWeighing?: () => Promise<void>;
}

/**
 * The prototype's "Simulate dispense / Simulate overshoot / Reset" buttons. They drive the
 * training scale for the component being weighed (TD-07); a real station has no such buttons.
 */
export function SimulationControls({ onSimulate, onResetWeighing }: SimulationProps) {
  const [note, run] = useAction();
  const title = onSimulate ? undefined : "Select a component to weigh first";
  return (
    <>
      {note && <span className="ctl-label">{note}</span>}
      <button
        type="button"
        className="btn primary"
        disabled={!onSimulate}
        title={title}
        onClick={() => onSimulate && void run(() => onSimulate("dispense"))}
      >
        ▶ Simulate dispense
      </button>
      <button
        type="button"
        className="btn"
        disabled={!onSimulate}
        title={title}
        onClick={() => onSimulate && void run(() => onSimulate("overshoot"))}
      >
        ▶ Simulate overshoot
      </button>
      <button
        type="button"
        className="btn"
        disabled={!onResetWeighing}
        title={title}
        onClick={() => onResetWeighing && void run(onResetWeighing)}
      >
        Reset
      </button>
    </>
  );
}

interface PanelProps {
  onTrainingReset: () => void;
}

/** Training bar: simulated scans, failure injection and data reset (TD-03, TD-05, TD-06). */
export function TrainingPanel({ onTrainingReset }: PanelProps) {
  const availability = useResource(() => api.training.availability());
  const [overrides, setOverrides] = useState<Record<string, boolean>>({});
  const [code, setCode] = useState("");
  const [note, run] = useAction();
  const systems = { ...availability.data?.systems, ...overrides };

  const toggle = (system: string, available: boolean) =>
    run(async () => setOverrides((await api.training.setAvailability(system, available)).systems));

  const reset = () =>
    run(async () => {
      await api.training.reset();
      setOverrides({});
      availability.reload();
      onTrainingReset();
    });

  return (
    <div className="controls" aria-label="Training panel">
      <span className="ctl-label">Training</span>
      <input
        className="training-input"
        aria-label="Code to scan"
        placeholder="Batch ID"
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <button type="button" className="btn" onClick={() => void run(() => api.training.scan(code))}>
        Simulate scan
      </button>
      <span className="spacer" />
      <span className="ctl-label">Available</span>
      {SYSTEMS.map(({ id, label }) => (
        <label key={id} className="toggle">
          <input
            type="checkbox"
            checked={systems[id] ?? true}
            onChange={(e) => void toggle(id, e.target.checked)}
          />
          {label}
        </label>
      ))}
      <button type="button" className="btn danger" onClick={() => void reset()}>
        Reset training data
      </button>
      {note && <span className="ctl-label">{note}</span>}
    </div>
  );
}
