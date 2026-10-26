import { useState } from "react";
import { api } from "../../api/client";
import type { Session, Ticket } from "../../api/types";
import { plainMessage } from "../../shared/messages";
import { formatHms } from "../../shared/time";
import { useFunctionKeys } from "../../shared/use-function-keys";
import { useResource } from "../../shared/use-resource";
import { TicketPreview } from "./TicketPreview";

interface Props {
  session: Session;
  onSessionChange: (session: Session) => void;
  onNextBatch: () => void;
}

/** Screen 3 · Confirm & print (FR-32, FR-16 – FR-18, FR-23). */
export function DoneScreen({ session, onSessionChange, onNextBatch }: Props) {
  const summary = useResource(() => api.summary(session.sessionId));
  const ticket = useResource(() => api.ticket(session.sessionId));
  const [note, setNote] = useState<{ text: string; error: boolean } | null>(null);
  /** The ticket as last printed; the preview shows it once something has been printed. */
  const [printed, setPrinted] = useState<Ticket | null>(null);
  const [busy, setBusy] = useState(false);

  const retrySync = async () => {
    setBusy(true);
    try {
      const updated = await api.sync(session.sessionId);
      onSessionChange(updated);
      summary.reload();
      if (updated.syncStatus !== "SYNCED") {
        setNote({ text: "OrgaTEX is still not reachable. Try again later.", error: true });
      } else {
        setNote(null);
      }
    } catch (e) {
      setNote({ text: plainMessage(e), error: true });
    } finally {
      setBusy(false);
    }
  };

  const print = async () => {
    setBusy(true);
    setNote(null);
    try {
      const result = await api.printTicket(session.sessionId);
      setNote({
        text: `${result.reprint ? "Reprint" : "Ticket"} printed · ${result.ticketId}`,
        error: false,
      });
      setPrinted(result.ticket);
    } catch (e) {
      setNote({ text: plainMessage(e), error: true });
    } finally {
      setBusy(false);
    }
  };

  useFunctionKeys({ F1: () => void print(), F3: onNextBatch }, !busy);

  const shownTicket = printed ?? ticket.data;
  const s = summary.data;
  const synced = s?.writeBack.status === "SYNCED";
  return (
    <div className="done-stage">
      <div className="done-msg">
        <span className="h">Batch {session.batchId} weighed</span>
        {summary.error !== undefined && (
          <div className="message error" role="alert">
            {plainMessage(summary.error)}
          </div>
        )}
        {s && (
          <>
            <div className="summary">
              <div className="r">
                <span className="k">Components weighed</span>
                <span className="v">
                  {s.componentsWeighed.done} of {s.componentsWeighed.total}
                </span>
              </div>
              <div className="r">
                <span className="k">All within tolerance</span>
                <span className={s.allWithinTolerance ? "v good" : "v warn"}>
                  {s.allWithinTolerance ? "YES" : `NO — ${s.overriddenCount} overridden`}
                </span>
              </div>
              <div className="r">
                <span className="k">Total dispensed</span>
                <span className="v">
                  {s.totalDispensed.value} {s.totalDispensed.unit}
                </span>
              </div>
              <div className="r">
                <span className="k">Elapsed</span>
                <span className="v">{s.elapsedText}</span>
              </div>
              <div className="r">
                <span className="k">Operator</span>
                <span className="v">{s.operatorName}</span>
              </div>
              <div className="r">
                <span className="k">Written to OrgaTEX</span>
                <span className={synced ? "v good" : "v warn"} data-testid="write-back">
                  {synced && s.writeBack.at ? `CONFIRMED ${formatHms(s.writeBack.at)}` : "PENDING"}
                </span>
              </div>
            </div>
            <table className="results" aria-label="Component results">
              <thead>
                <tr>
                  <th>Component</th>
                  <th>Target</th>
                  <th>Actual</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                {s.results.map((r) => (
                  <tr key={r.componentId}>
                    <td>{r.name}</td>
                    <td className="n">
                      {r.target.value} {r.target.unit}
                    </td>
                    <td className="n">{r.actual ? `${r.actual.value} ${r.actual.unit}` : "—"}</td>
                    <td className={r.result === "IN_TOLERANCE" ? "ok" : "warn"}>
                      {r.result === "IN_TOLERANCE" ? "IN TOLERANCE" : (r.result ?? "—")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p style={{ margin: 0, fontSize: 13.5, color: "var(--hmi-muted)" }}>
              {synced
                ? `Actual consumption posted against the batch. Container released for transport to ${s.machineRef}.`
                : "Actual consumption is stored at the station but not yet written to OrgaTEX."}
            </p>
            {!synced && (
              <div className="message error" role="alert">
                OrgaTEX has not received the consumption yet.
                <button
                  type="button"
                  className="key"
                  disabled={busy}
                  onClick={() => void retrySync()}
                >
                  Retry
                </button>
              </div>
            )}
          </>
        )}
        {note && (
          <div className={note.error ? "message error" : "message info"} role="status">
            {note.text}
          </div>
        )}
        <div className="actions">
          <button
            type="button"
            className="key ok"
            disabled={busy || ticket.data === undefined}
            onClick={() => void print()}
          >
            Print ticket<span className="fn">F1</span>
          </button>
          <button type="button" className="key" onClick={onNextBatch}>
            Next batch<span className="fn">F3</span>
          </button>
        </div>
      </div>
      <div>{shownTicket && <TicketPreview ticket={shownTicket} />}</div>
    </div>
  );
}
