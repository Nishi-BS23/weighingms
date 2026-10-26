import { useState } from "react";
import { api } from "../../api/client";
import type { Session } from "../../api/types";
import { plainMessage } from "../../shared/messages";
import { useFunctionKeys } from "../../shared/use-function-keys";
import { usePolling } from "../../shared/use-polling";
import { RecipeRail } from "./RecipeRail";
import { OverrideDialog, QuitDialog } from "./WeighingDialogs";
import { Readout, SurplusPanel, ToleranceBar, WeighHeader } from "./WeighingPanel";

const LIVE_POLL_MS = 120;

interface Props {
  session: Session;
  onSessionChange: (session: Session) => void;
  onQuit: () => void;
}

/** Screen 2 · Weigh (FR-31). Every rule-based value comes from the session API. */
export function WeighScreen({ session, onSessionChange, onQuit }: Props) {
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dialog, setDialog] = useState<"quit" | "override" | null>(null);

  const weighing = session.status === "IN_PROGRESS" && session.activeComponentId !== null;
  // Paused while an action runs: a poll racing the final confirm would hit a completed session.
  const polled = usePolling(
    (signal) => api.live(session.sessionId, signal),
    LIVE_POLL_MS,
    weighing && !busy,
  );
  const component = session.components.find((c) => c.componentId === session.activeComponentId);
  const live = polled.data?.componentId === component?.componentId ? polled.data : undefined;

  const run = async (action: () => Promise<Session | void>) => {
    setBusy(true);
    setMessage(null);
    try {
      const updated = await action();
      if (updated) onSessionChange(updated);
    } catch (e) {
      setMessage(plainMessage(e));
    } finally {
      setBusy(false);
      polled.refresh();
    }
  };

  const canConfirm = Boolean(live?.canConfirm) && !busy;
  const confirm = () => void run(() => api.confirm(session.sessionId));
  const retare = () =>
    void run(async () => {
      await api.retare(session.sessionId);
    });

  useFunctionKeys(
    {
      F1: () => {
        if (canConfirm) confirm();
      },
      F2: () => {
        if (weighing && !busy) retare();
      },
      F4: () => {
        if (weighing && !busy) setDialog("quit");
      },
    },
    dialog === null,
  );

  return (
    <>
      <div className="stage">
        <RecipeRail
          session={session}
          disabled={busy}
          onActivate={(cid) => void run(() => api.activate(session.sessionId, cid))}
        />
        <section className="weigh">
          {component && session.active ? (
            <>
              <WeighHeader component={component} active={session.active} />
              <Readout component={component} live={live} />
              <ToleranceBar
                component={component}
                active={session.active}
                live={live}
                overrideRequested={dialog === "override"}
              />
              <SurplusPanel live={live} unit={component.target.unit} />
            </>
          ) : (
            <div className="message info">Select a component in the recipe to weigh it.</div>
          )}
          {message && (
            <div className="message error" role="alert">
              {message}
            </div>
          )}
          <div className="actions">
            <button type="button" className="key ok" disabled={!canConfirm} onClick={confirm}>
              OK · Confirm<span className="fn">F1</span>
            </button>
            <button type="button" className="key" disabled={!weighing || busy} onClick={retare}>
              Re-tare<span className="fn">F2</span>
            </button>
            <button
              type="button"
              className="key ghost"
              disabled={!weighing || busy}
              onClick={() => setDialog("quit")}
            >
              Quit<span className="fn">F4</span>
            </button>
            <button
              type="button"
              className="key ghost"
              style={{ marginLeft: "auto" }}
              disabled={!weighing || busy}
              onClick={() => setDialog("override")}
            >
              Supervisor override
            </button>
          </div>
        </section>
      </div>

      {dialog === "quit" && component && (
        <QuitDialog
          componentName={component.name}
          onCancel={() => setDialog(null)}
          onConfirm={async () => {
            await api.quit(session.sessionId);
            setDialog(null);
            onQuit();
          }}
        />
      )}
      {dialog === "override" && (
        <OverrideDialog
          onCancel={() => setDialog(null)}
          onSubmit={async (pin, reason) => {
            const updated = await api.override(session.sessionId, pin, reason);
            setDialog(null);
            onSessionChange(updated);
          }}
        />
      )}
    </>
  );
}
