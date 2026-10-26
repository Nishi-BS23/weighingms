export type Step = "queue" | "weigh" | "done";

const STEPS: { step: Step; label: string }[] = [
  { step: "queue", label: "1 · Select batch" },
  { step: "weigh", label: "2 · Weigh" },
  { step: "done", label: "3 · Confirm & print" },
];

interface Props {
  current: Step;
  reachable: Record<Step, boolean>;
  onSelect: (step: Step) => void;
}

/** The prototype's screen switcher, as a workflow step indicator (TA-20). */
export function StepIndicator({ current, reachable, onSelect }: Props) {
  return (
    <>
      <span className="ctl-label">Screen</span>
      <div className="seg" role="group" aria-label="Screen">
        {STEPS.map(({ step, label }) => (
          <button
            key={step}
            type="button"
            aria-pressed={current === step}
            disabled={!reachable[step]}
            onClick={() => onSelect(step)}
          >
            {label}
          </button>
        ))}
      </div>
    </>
  );
}
