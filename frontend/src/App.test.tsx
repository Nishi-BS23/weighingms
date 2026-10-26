import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { batch, deviceStatus, queue } from "./test-fixtures";
import { stubApi } from "./test-utils";

afterEach(() => {
  vi.unstubAllGlobals();
});

const operator = (name: string) => ({
  operatorId: "OP-1001",
  name,
  shift: "Shift A",
  role: "OPERATOR",
});

describe("App", () => {
  it("reloads the queue and the operator after a training reset", async () => {
    let reset = false;
    const { calls } = stubApi({
      "GET /api/batches": () => ({
        body: queue([
          batch(reset ? {} : { status: "WEIGHED", selectable: false, notSelectableReason: "Done" }),
        ]),
      }),
      "GET /api/operators/current": () => ({ body: operator(reset ? "R. Karim" : "M. Hossain") }),
      "GET /api/devices/status": { body: deviceStatus() },
      "GET /api/scanner/scans": { body: { scans: [], lastSeq: 0 } },
      "GET /api/training/availability": { body: { systems: { orgatex: true } } },
      "POST /api/training/reset": () => {
        reset = true;
        return { body: { reset: true } };
      },
    });
    render(<App />);
    const row = async () => (await screen.findByText("B-24187")).closest("tr")!;
    expect(within(await row()).getByText("WEIGHED")).toBeInTheDocument();
    expect(await screen.findByText("M. Hossain")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Reset training data" }));

    expect(await within(await row()).findByText("QUEUED")).toBeInTheDocument();
    expect(await screen.findByText("R. Karim")).toBeInTheDocument();
    expect(calls.filter((c) => c === "GET /api/batches")).toHaveLength(2);
  });
});
