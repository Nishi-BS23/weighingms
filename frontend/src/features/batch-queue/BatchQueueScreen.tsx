import { useCallback, useState } from "react";
import { api } from "../../api/client";
import type { Batch, Recipe } from "../../api/types";
import { errorCode, plainMessage } from "../../shared/messages";
import { useResource } from "../../shared/use-resource";
import { QueueTable } from "./QueueTable";
import { ScanPrompt } from "./ScanPrompt";
import { useScanner } from "./use-scanner";

interface Props {
  /** Called once the batch and its recipe have been loaded from the API (Workbook Step 19). */
  onSelected: (batch: Batch, recipe: Recipe) => void | Promise<void>;
}

/** Screen 1 · Select batch (FR-30, FR-1, FR-2). All data comes from the WeighingMS API. */
export function BatchQueueScreen({ onSelected }: Props) {
  const queue = useResource((signal) => api.batches(signal));
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const select = useCallback(
    async (code: string) => {
      if (busy) return;
      setBusy(true);
      setMessage(null);
      try {
        const batch = await api.batch(code);
        if (!batch.selectable) {
          setMessage(
            `Batch ${batch.batchId} cannot be weighed: ${batch.notSelectableReason ?? ""}`,
          );
          return;
        }
        const recipe = await api.recipe(batch.batchId);
        await onSelected(batch, recipe);
      } catch (e) {
        setMessage(
          errorCode(e) === "BATCH_NOT_FOUND"
            ? `Batch ${code} cannot be weighed: it is not in the OrgaTEX queue.`
            : plainMessage(e),
        );
      } finally {
        setBusy(false);
      }
    },
    [busy, onSelected],
  );

  const scanner = useScanner((code) => void select(code), true);

  return (
    <div className="queue">
      <ScanPrompt
        receivedAt={queue.data?.receivedAt}
        scannerAvailable={scanner.available}
        onCode={(code) => void select(code)}
      />
      {message && (
        <div className="message error" role="alert">
          {message}
        </div>
      )}
      {queue.error !== undefined ? (
        <div className="message error" role="alert">
          {plainMessage(queue.error)}
          <button type="button" className="key" onClick={queue.reload}>
            Retry
          </button>
        </div>
      ) : queue.data ? (
        <QueueTable batches={queue.data.batches} onSelect={(b) => void select(b.batchId)} />
      ) : (
        <div className="empty">Loading the batch queue from OrgaTEX…</div>
      )}
    </div>
  );
}
