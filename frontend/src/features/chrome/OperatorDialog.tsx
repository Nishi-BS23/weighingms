import { useState, type FormEvent } from "react";
import { api } from "../../api/client";
import type { Operator } from "../../api/types";
import { Dialog } from "../../shared/Dialog";
import { plainMessage } from "../../shared/messages";

interface Props {
  onSignedIn: (operator: Operator) => void;
  onCancel: () => void;
}

/** Change the operator at the station by badge (FR-19, TA-09). */
export function OperatorDialog({ onSignedIn, onCancel }: Props) {
  const [badge, setBadge] = useState("");
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      onSignedIn(await api.signIn(badge.trim()));
    } catch (err) {
      setError(plainMessage(err));
    }
  };

  return (
    <Dialog title="Change operator" onCancel={onCancel}>
      <form
        onSubmit={(e) => void submit(e)}
        style={{ display: "flex", flexDirection: "column", gap: 14 }}
      >
        <p>Scan or type your badge number.</p>
        <label>
          Badge
          <input autoFocus value={badge} onChange={(e) => setBadge(e.target.value)} />
        </label>
        {error && (
          <span className="error-text" role="alert">
            {error}
          </span>
        )}
        <div className="actions">
          <button type="submit" className="key ok" disabled={!badge.trim()}>
            Sign in
          </button>
          <button type="button" className="key ghost" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </Dialog>
  );
}
