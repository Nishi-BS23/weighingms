import { useCallback, useEffect, useRef, useState } from "react";

export interface Polled<T> {
  data: T | undefined;
  error: unknown;
  refresh: () => void;
}

/**
 * Calls `fetcher` every `intervalMs` while `enabled`. A new call starts only after the previous
 * one finished, so a slow backend is never flooded. Unmounting aborts the call in flight.
 */
export function usePolling<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  intervalMs: number,
  enabled = true,
): Polled<T> {
  const [data, setData] = useState<T>();
  const [error, setError] = useState<unknown>();
  const [tick, setTick] = useState(0);
  const fetcherRef = useRef(fetcher);

  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  useEffect(() => {
    if (!enabled) return;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;

    const run = async () => {
      try {
        const result = await fetcherRef.current(controller.signal);
        if (controller.signal.aborted) return;
        setData(result);
        setError(undefined);
      } catch (e) {
        if (controller.signal.aborted) return;
        setError(e);
      }
      timer = setTimeout(() => void run(), intervalMs);
    };
    void run();

    return () => {
      controller.abort();
      if (timer) clearTimeout(timer);
    };
  }, [intervalMs, enabled, tick]);

  const refresh = useCallback(() => setTick((t) => t + 1), []);
  return { data, error, refresh };
}
