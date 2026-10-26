import type { Operator } from "../../api/types";

export interface BatchCrumb {
  batchId: string;
  orderRef: string;
  machineRef: string;
}

interface Props {
  stationName: string;
  batch: BatchCrumb | null;
  operator: Operator | null;
  onOperatorClick?: () => void;
}

export function TopBar({ stationName, batch, operator, onOperatorClick }: Props) {
  return (
    <div className="topbar">
      <span className="brandmark">
        <span className="n">WeighingMS</span>
        <span className="s">{stationName}</span>
      </span>
      {batch && (
        <span className="crumb" data-testid="crumb">
          BATCH <b>{batch.batchId}</b> · ORDER <b>{batch.orderRef}</b> · MACHINE{" "}
          <b>{batch.machineRef}</b>
        </span>
      )}
      <span className="spacer" />
      <button type="button" className="op-chip" onClick={onOperatorClick} title="Change operator">
        <span className={operator ? "dot" : "dot none"} />
        Operator&nbsp;<b>{operator ? operator.name : "—"}</b>
        {operator && <> · {operator.shift}</>}
      </button>
    </div>
  );
}
