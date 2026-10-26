import type { Batch } from "../../api/types";

const TAG_CLASS: Record<string, string> = { WEIGHING: "tag now", WEIGHED: "tag done" };

interface Props {
  batches: Batch[];
  onSelect: (batch: Batch) => void;
}

export function QueueTable({ batches, onSelect }: Props) {
  if (batches.length === 0) {
    return <div className="empty">No batches released to this station.</div>;
  }
  return (
    <div style={{ overflowX: "auto" }}>
      <table className="q">
        <thead>
          <tr>
            <th>Batch</th>
            <th>Order</th>
            <th>Machine</th>
            <th>Fabric / lot</th>
            <th>Shade</th>
            <th>Comp.</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {batches.map((b) => {
            const classes = [b.status === "WEIGHING" ? "sel" : "", b.selectable ? "" : "blocked"];
            return (
              <tr
                key={b.batchId}
                className={classes.join(" ").trim() || undefined}
                tabIndex={0}
                data-batch={b.batchId}
                title={b.notSelectableReason ?? undefined}
                onClick={() => onSelect(b)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") onSelect(b);
                }}
              >
                <td className="mono">{b.batchId}</td>
                <td className="mono">{b.orderRef}</td>
                <td className="mono">{b.machineRef}</td>
                <td>{b.fabricLot}</td>
                <td>{b.shadeCode}</td>
                <td className="mono">{b.componentCount}</td>
                <td>
                  <span className={TAG_CLASS[b.status] ?? "tag"}>{b.status}</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
