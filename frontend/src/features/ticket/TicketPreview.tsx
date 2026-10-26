import type { Ticket } from "../../api/types";
import { barcodeBars } from "./barcode";

const pad = (text: string, width: number) => text.padEnd(width, " ");
const left = (text: string, width: number) => text.padStart(width, " ");

/** Paper-style preview of the weighing ticket (prototype `.ticket`, FR-18). */
export function TicketPreview({ ticket }: { ticket: Ticket }) {
  return (
    <div className="ticket" data-testid="ticket">
      <div className="c bold">{ticket.header}</div>
      {ticket.reprint && <div className="c bold">*** REPRINT ***</div>}
      <hr />
      {`BATCH   ${ticket.batchId}\nORDER   ${ticket.orderRef}\nMACHINE ${ticket.machineRef}\nSHADE   ${ticket.shadeCode}\nDATE    ${ticket.date}\nOPER.   ${ticket.operatorName}`}
      <hr />
      <span className="bold">{`${pad("COMPONENT", 12)}${left("TGT", 7)}${left("ACT", 7)}`}</span>
      {"\n"}
      {ticket.lines
        .map(
          (line) =>
            `${pad(line.shortName + (line.overridden ? "*" : ""), 12)}${left(line.target.value, 7)}${left(line.actual.value, 7)} ${line.target.unit}`,
        )
        .join("\n")}
      <hr />
      <div className="c">{ticket.resultLine}</div>
      <div className="barcode" aria-hidden="true">
        {barcodeBars(ticket.barcodeValue).map((bar, i) => (
          <i key={i} className={bar.gap ? "gap" : undefined} style={{ width: `${bar.width}px` }} />
        ))}
      </div>
      <div className="c">{ticket.barcodeValue}</div>
    </div>
  );
}
