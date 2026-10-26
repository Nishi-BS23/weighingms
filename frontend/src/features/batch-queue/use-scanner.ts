import { useEffect, useRef } from "react";
import { api } from "../../api/client";
import { usePolling } from "../../shared/use-polling";

const SCAN_POLL_MS = 300;

/**
 * Delivers each new barcode scan to `onScan` exactly once. Scans made before the screen opened are
 * ignored (the first poll only records the cursor).
 */
export function useScanner(
  onScan: (code: string) => void,
  enabled: boolean,
): { available: boolean } {
  const cursor = useRef<number | null>(null);
  const onScanRef = useRef(onScan);

  useEffect(() => {
    onScanRef.current = onScan;
  });

  const { error } = usePolling(
    async (signal) => {
      const batch = await api.scans(cursor.current ?? 0, signal);
      if (cursor.current === null) {
        cursor.current = batch.lastSeq;
        return batch;
      }
      cursor.current = batch.lastSeq;
      for (const scan of batch.scans) onScanRef.current(scan.code);
      return batch;
    },
    SCAN_POLL_MS,
    enabled,
  );

  return { available: error === undefined };
}
