import type { Session, SessionComponent } from "../../api/types";

/** "3 kg precision" → "3 kg", as on the prototype's rail. */
const scaleShort = (label: string) => label.split(" ").slice(0, 2).join(" ");

function stateText(c: SessionComponent): string {
  if (c.state === "DONE") return `✓ ${c.actual?.value ?? ""}`;
  return c.state === "ACTIVE" ? "WEIGHING" : "PENDING";
}

interface Props {
  session: Session;
  disabled: boolean;
  onActivate: (componentId: string) => void;
}

/** Recipe rail with done / weighing / pending components (FR-3, FR-15; prototype `.rail`). */
export function RecipeRail({ session, disabled, onActivate }: Props) {
  return (
    <aside className="rail">
      <div className="rail-head">
        <span className="t">Recipe · {session.shadeCode}</span>
        <span className="v">{session.batchId}</span>
        <span className="m">
          {session.progress.done} of {session.progress.total} components weighed
        </span>
      </div>
      <ul className="comps">
        {session.components.map((c) => (
          <li key={c.componentId}>
            <button
              type="button"
              className="comp"
              data-state={c.state.toLowerCase()}
              data-component={c.componentId}
              aria-disabled={c.state !== "PENDING"}
              onClick={() => {
                if (c.state === "PENDING" && !disabled) onActivate(c.componentId);
              }}
            >
              <span className="swatch" style={{ background: c.colourHex }} />
              <span>
                <span className="nm">{c.name}</span>
                <br />
                <span className="sub">
                  {c.dyestuffCode} · {scaleShort(c.scale.label)}
                </span>
              </span>
              <span>
                <span className="qty">
                  {c.target.value} {c.target.unit}
                </span>
                <br />
                <span className="st">{stateText(c)}</span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
