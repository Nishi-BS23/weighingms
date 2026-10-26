import { useEffect, useRef } from "react";

export type FunctionKey = "F1" | "F2" | "F3" | "F4";

/**
 * The industrial terminal's function keys (Brief IR-17). Handlers run only while `enabled`
 * (e.g. not while a dialog is open); handled keys never reach the browser (F1 = help, F3 = find).
 */
export function useFunctionKeys(
  handlers: Partial<Record<FunctionKey, () => void>>,
  enabled: boolean,
): void {
  const handlersRef = useRef(handlers);
  useEffect(() => {
    handlersRef.current = handlers;
  });

  useEffect(() => {
    if (!enabled) return;
    const onKey = (event: KeyboardEvent) => {
      const handler = handlersRef.current[event.key as FunctionKey];
      if (handler) {
        event.preventDefault();
        handler();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [enabled]);
}
