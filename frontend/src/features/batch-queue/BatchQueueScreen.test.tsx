import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { batch, queue, recipe } from "../../test-fixtures";
import { apiError, stubApi } from "../../test-utils";
import { BatchQueueScreen } from "./BatchQueueScreen";

const QUEUE = queue([
  batch(),
  batch({ batchId: "B-24190", shadeCode: "Navy 12", fabricLot: "CVC fleece · 310 kg" }),
  batch({
    batchId: "B-24188",
    status: "WEIGHED",
    selectable: false,
    notSelectableReason: "Batch has already been weighed.",
  }),
]);

const NO_SCANS = { body: { scans: [], lastSeq: 0 } };

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("BatchQueueScreen", () => {
  it("renders the queue from GET /api/batches", async () => {
    const { calls } = stubApi({
      "GET /api/batches": { body: QUEUE },
      "GET /api/scanner/scans": NO_SCANS,
    });
    render(<BatchQueueScreen onSelected={vi.fn()} />);

    const row = (await screen.findByText("B-24190")).closest("tr")!;
    expect(within(row).getByText("CVC fleece · 310 kg")).toBeInTheDocument();
    expect(within(row).getByText("Navy 12")).toBeInTheDocument();
    expect(calls).toContain("GET /api/batches");
    expect(screen.getByText(/Queue received from OrgaTEX at/)).toBeInTheDocument();
  });

  it("loads batch and recipe when a row is touched", async () => {
    const { calls } = stubApi({
      "GET /api/batches": { body: QUEUE },
      "GET /api/batches/B-24187": { body: batch() },
      "GET /api/batches/B-24187/recipe": { body: recipe() },
      "GET /api/scanner/scans": NO_SCANS,
    });
    const onSelected = vi.fn();
    render(<BatchQueueScreen onSelected={onSelected} />);

    await userEvent.click(await screen.findByText("B-24187"));

    await waitFor(() => expect(onSelected).toHaveBeenCalledTimes(1));
    expect(onSelected.mock.calls[0]?.[1]).toEqual(recipe());
    expect(calls).toEqual(
      expect.arrayContaining(["GET /api/batches/B-24187", "GET /api/batches/B-24187/recipe"]),
    );
  });

  it("explains why a batch cannot be weighed", async () => {
    stubApi({
      "GET /api/batches": { body: QUEUE },
      "GET /api/batches/B-24188": { body: QUEUE.batches[2] },
      "GET /api/scanner/scans": NO_SCANS,
    });
    const onSelected = vi.fn();
    render(<BatchQueueScreen onSelected={onSelected} />);

    await userEvent.click(await screen.findByText("B-24188"));

    expect(
      await screen.findByText("Batch B-24188 cannot be weighed: Batch has already been weighed."),
    ).toBeInTheDocument();
    expect(onSelected).not.toHaveBeenCalled();
  });

  it("accepts a keyboard-wedge scan and explains an unknown code", async () => {
    stubApi({
      "GET /api/batches": { body: QUEUE },
      "GET /api/batches/B-99999": apiError(404, "BATCH_NOT_FOUND"),
      "GET /api/scanner/scans": NO_SCANS,
    });
    render(<BatchQueueScreen onSelected={vi.fn()} />);
    await screen.findByText("B-24187");

    await userEvent.type(screen.getByLabelText("Scan or type a batch ID"), "B-99999{Enter}");

    expect(
      await screen.findByText("Batch B-99999 cannot be weighed: it is not in the OrgaTEX queue."),
    ).toBeInTheDocument();
  });

  it("selects a batch scanned on the barcode scanner", async () => {
    let lastSeq = 0;
    stubApi({
      "GET /api/batches": { body: QUEUE },
      "GET /api/batches/B-24190": { body: QUEUE.batches[1] },
      "GET /api/batches/B-24190/recipe": { body: recipe("B-24190") },
      "GET /api/scanner/scans": () =>
        lastSeq === 0
          ? { body: { scans: [], lastSeq: 0 } }
          : { body: { scans: [{ seq: 1, code: "B-24190", scannedAt: "x" }], lastSeq: 1 } },
    });
    const onSelected = vi.fn();
    render(<BatchQueueScreen onSelected={onSelected} />);
    await screen.findByText("B-24187");
    await new Promise((resolve) => setTimeout(resolve, 350));

    lastSeq = 1;

    await waitFor(() => expect(onSelected).toHaveBeenCalledTimes(1), { timeout: 2000 });
    expect(onSelected.mock.calls[0]?.[0]).toMatchObject({ batchId: "B-24190" });
  });

  it("shows a plain message and a Retry when OrgaTEX is down", async () => {
    let orgatexUp = false;
    stubApi({
      "GET /api/batches": () =>
        orgatexUp ? { body: QUEUE } : apiError(503, "ORGATEX_UNAVAILABLE"),
      "GET /api/scanner/scans": NO_SCANS,
    });
    render(<BatchQueueScreen onSelected={vi.fn()} />);

    expect(
      await screen.findByText("OrgaTEX is not reachable. Check the connection and retry."),
    ).toBeInTheDocument();
    expect(screen.queryByText("B-24187")).not.toBeInTheDocument();

    orgatexUp = true;
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByText("B-24187")).toBeInTheDocument();
  });

  it("tells the operator to touch a row when the scanner is down", async () => {
    stubApi({
      "GET /api/batches": { body: QUEUE },
      "GET /api/scanner/scans": apiError(503, "SCANNER_UNAVAILABLE"),
    });
    render(<BatchQueueScreen onSelected={vi.fn()} />);

    expect(
      await screen.findByText("Scanner unavailable — touch a row to select a batch."),
    ).toBeInTheDocument();
  });
});
