import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ticket } from "../../test-fixtures";
import { barcodeBars } from "./barcode";
import { TicketPreview } from "./TicketPreview";

describe("TicketPreview", () => {
  it("shows the prototype ticket fields", () => {
    render(<TicketPreview ticket={ticket()} />);
    const preview = screen.getByTestId("ticket");

    expect(preview).toHaveTextContent("FCI DYEING — WEIGHING TICKET");
    expect(preview).toHaveTextContent("BATCH B-24187");
    expect(preview).toHaveTextContent("MACHINE JET-04");
    expect(preview).toHaveTextContent("OPER. R. Karim");
    expect(preview).toHaveTextContent("Blue RSPL 1240.0 1241.5 g");
    expect(preview).toHaveTextContent("Soda Ash 9.600 9.621 kg");
    expect(preview).toHaveTextContent("ALL WITHIN TOLERANCE");
    expect(preview.querySelectorAll(".barcode i")).toHaveLength(barcodeBars("B-24187").length);
    expect(screen.queryByText("*** REPRINT ***")).not.toBeInTheDocument();
  });

  it("marks reprints and overridden components", () => {
    const reprint = ticket({
      reprint: true,
      resultLine: "1 OVERRIDDEN (*)",
      lines: [
        {
          shortName: "Yellow RGB",
          target: { value: "94.0", unit: "g" },
          actual: { value: "96.4", unit: "g" },
          overridden: true,
        },
      ],
    });
    render(<TicketPreview ticket={reprint} />);

    expect(screen.getByText("*** REPRINT ***")).toBeInTheDocument();
    expect(screen.getByTestId("ticket")).toHaveTextContent("Yellow RGB* 94.0 96.4 g");
    expect(screen.getByText("1 OVERRIDDEN (*)")).toBeInTheDocument();
  });
});

describe("barcodeBars", () => {
  it("is deterministic per value", () => {
    expect(barcodeBars("B-24187")).toEqual(barcodeBars("B-24187"));
    expect(barcodeBars("B-24187")).not.toEqual(barcodeBars("B-24188"));
  });
});
