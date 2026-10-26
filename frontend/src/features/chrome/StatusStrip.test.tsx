import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { deviceStatus } from "../../test-fixtures";
import { formatHm } from "../../shared/time";
import { StatusStrip } from "./StatusStrip";

describe("StatusStrip", () => {
  it("shows every device as in the prototype when all are up", () => {
    render(<StatusStrip status={deviceStatus()} />);

    expect(screen.getByText("SCALE 3 kg · READY")).toBeInTheDocument();
    expect(screen.getByText("SCALE 32 kg · READY")).toBeInTheDocument();
    expect(screen.getByText("SCANNER")).toBeInTheDocument();
    expect(screen.getByText("PRINTER")).toBeInTheDocument();
    expect(
      screen.getByText(`ORGATEX · LINKED ${formatHm("2026-10-26T07:41:00Z")}`),
    ).toBeInTheDocument();
    expect(screen.getByText("EN")).toBeInTheDocument();
  });

  it("marks failed and degraded devices with text, not only colour", () => {
    const status = deviceStatus({
      devices: [
        { device: "scale-3kg", label: "SCALE 3 kg", state: "DEGRADED", text: "CAL EXPIRED" },
        { device: "scale-32kg", label: "SCALE 32 kg", state: "DOWN", text: "OFFLINE" },
        { device: "scanner", label: "SCANNER", state: "DOWN", text: "OFFLINE" },
        { device: "printer", label: "PRINTER", state: "UP", text: "READY" },
        { device: "orgatex", label: "ORGATEX", state: "DOWN", text: "OFFLINE" },
      ],
    });
    render(<StatusStrip status={status} />);

    expect(screen.getByText("SCALE 3 kg · CAL EXPIRED").closest(".stat")).toHaveAttribute(
      "data-state",
      "DEGRADED",
    );
    expect(screen.getByText("SCALE 32 kg · OFFLINE")).toBeInTheDocument();
    expect(screen.getByText("SCANNER · OFFLINE")).toBeInTheDocument();
    expect(screen.getByText("ORGATEX · OFFLINE")).toBeInTheDocument();
  });

  it("says when device status is unknown", () => {
    render(<StatusStrip status={undefined} />);

    expect(screen.getByText("DEVICE STATUS UNKNOWN")).toBeInTheDocument();
  });
});
