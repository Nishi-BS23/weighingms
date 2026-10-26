import { useState, type FormEvent } from "react";
import { Dialog } from "../../shared/Dialog";
import { plainMessage } from "../../shared/messages";

interface QuitProps {
  componentName: string;
  onConfirm: () => Promise<void>;
  onCancel: () => void;
}

/** Quit (F4): abandon the component being weighed and leave the batch (FR-22). */
export function QuitDialog({ componentName, onConfirm, onCancel }: QuitProps) {
  const [error, setError] = useState<string | null>(null);
  return (
    <Dialog title={`Abandon ${componentName}?`} onCancel={onCancel}>
      <p>
        Nothing will be recorded for it. Components already weighed are kept, and the batch can be
        resumed from the queue.
      </p>
      {error && <span className="error-text">{error}</span>}
      <div className="actions">
        <button
          type="button"
          className="key"
          onClick={() => void onConfirm().catch((e: unknown) => setError(plainMessage(e)))}
        >
          Quit
        </button>
        <button type="button" className="key ghost" onClick={onCancel}>
          Keep weighing
        </button>
      </div>
    </Dialog>
  );
}

interface OverrideProps {
  onSubmit: (pin: string, reason: string) => Promise<void>;
  onCancel: () => void;
}

/** Supervisor override: PIN + mandatory reason (FR-21). The PIN never leaves this request. */
export function OverrideDialog({ onSubmit, onCancel }: OverrideProps) {
  const [pin, setPin] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!reason.trim()) {
      setError("Enter the reason for the override.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onSubmit(pin, reason.trim());
    } catch (err) {
      setError(plainMessage(err));
      setPin("");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Dialog title="Supervisor override" onCancel={onCancel}>
      <form
        onSubmit={(e) => void submit(e)}
        style={{ display: "flex", flexDirection: "column", gap: 14 }}
      >
        <p>A supervisor can accept this weighing outside tolerance. It will be recorded.</p>
        <label>
          Supervisor PIN
          <input
            type="password"
            inputMode="numeric"
            autoComplete="off"
            autoFocus
            value={pin}
            onChange={(e) => setPin(e.target.value)}
          />
        </label>
        <label>
          Reason
          <textarea rows={2} value={reason} onChange={(e) => setReason(e.target.value)} />
        </label>
        {error && (
          <span className="error-text" role="alert">
            {error}
          </span>
        )}
        <div className="actions">
          <button type="submit" className="key ok" disabled={busy || !pin}>
            Authorise
          </button>
          <button type="button" className="key ghost" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </Dialog>
  );
}
