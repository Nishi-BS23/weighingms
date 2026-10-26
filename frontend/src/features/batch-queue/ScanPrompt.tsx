import { useState } from "react";
import { formatHm } from "../../shared/time";

interface Props {
  receivedAt: string | undefined;
  scannerAvailable: boolean;
  onCode: (code: string) => void;
}

/**
 * "Scan a batch card to begin". The field also accepts keyboard-wedge scanners, which type the
 * code followed by Enter into the focused field.
 */
export function ScanPrompt({ receivedAt, scannerAvailable, onCode }: Props) {
  const [value, setValue] = useState("");

  return (
    <div className="scan-prompt">
      <div className={scannerAvailable ? "beam" : "beam off"} aria-hidden="true" />
      <div>
        <div className="big">Scan a batch card to begin</div>
        {scannerAvailable ? (
          <div className="sm">
            Or touch a row below.
            {receivedAt && <> Queue received from OrgaTEX at {formatHm(receivedAt)}.</>}
          </div>
        ) : (
          <div className="sm warn">Scanner unavailable — touch a row to select a batch.</div>
        )}
      </div>
      <input
        className="scan-field"
        aria-label="Scan or type a batch ID"
        placeholder="Batch ID"
        value={value}
        autoFocus
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && value.trim()) {
            onCode(value.trim());
            setValue("");
          }
        }}
      />
    </div>
  );
}
