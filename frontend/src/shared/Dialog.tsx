import { useEffect, type ReactNode } from "react";

interface Props {
  title: string;
  onCancel: () => void;
  children: ReactNode;
}

/** Modal dialog drawn inside the device screen. Escape cancels. */
export function Dialog({ title, onCancel, children }: Props) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div className="dialog-backdrop">
      <div className="dialog" role="dialog" aria-modal="true" aria-label={title}>
        <h2>{title}</h2>
        {children}
      </div>
    </div>
  );
}
