import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { session, summary, ticket } from "../../test-fixtures";
import { apiError, stubApi } from "../../test-utils";
import { formatHms } from "../../shared/time";
import { DoneScreen } from "./DoneScreen";

afterEach(() => {
  vi.unstubAllGlobals();
});

const completed = session({ status: "COMPLETED", syncStatus: "SYNCED" });

describe("DoneScreen", () => {
  it("shows the prototype's completion summary and the results per component", async () => {
    stubApi({
      "GET /api/sessions/WS-1/summary": { body: summary() },
      "GET /api/sessions/WS-1/ticket": { body: ticket() },
    });
    render(<DoneScreen session={completed} onSessionChange={vi.fn()} onNextBatch={vi.fn()} />);

    expect(screen.getByText("Batch B-24187 weighed")).toBeInTheDocument();
    expect(await screen.findByText("5 of 5")).toBeInTheDocument();
    expect(screen.getByText("YES")).toBeInTheDocument();
    expect(screen.getByText("35.322 kg")).toBeInTheDocument();
    expect(screen.getByText("6 min 41 s")).toBeInTheDocument();
    expect(screen.getByText("R. Karim")).toBeInTheDocument();
    expect(screen.getByTestId("write-back")).toHaveTextContent(
      `CONFIRMED ${formatHms("2026-10-26T07:48:22Z")}`,
    );
    const results = screen.getByRole("table", { name: "Component results" });
    expect(within(results).getByText("Soda Ash")).toBeInTheDocument();
    expect(within(results).getByText("9.621 kg")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Actual consumption posted against the batch. Container released for transport to JET-04.",
      ),
    ).toBeInTheDocument();
  });

  it("offers a Retry when the write-back is pending", async () => {
    let synced = false;
    const pending = summary({ writeBack: { status: "PENDING", at: null, consumptionId: null } });
    const { calls } = stubApi({
      "GET /api/sessions/WS-1/summary": () => ({ body: synced ? summary() : pending }),
      "GET /api/sessions/WS-1/ticket": { body: ticket() },
      "POST /api/sessions/WS-1/sync": () => {
        synced = true;
        return { body: completed };
      },
    });
    const onSessionChange = vi.fn();
    render(
      <DoneScreen
        session={session({ status: "COMPLETED", syncStatus: "PENDING" })}
        onSessionChange={onSessionChange}
        onNextBatch={vi.fn()}
      />,
    );

    expect(await screen.findByTestId("write-back")).toHaveTextContent("PENDING");
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));

    await waitFor(() => expect(screen.getByTestId("write-back")).toHaveTextContent("CONFIRMED"));
    expect(calls).toContain("POST /api/sessions/WS-1/sync");
    expect(onSessionChange).toHaveBeenCalledWith(completed);
  });

  it("prints the ticket and shows the ticket as printed", async () => {
    stubApi({
      "GET /api/sessions/WS-1/summary": { body: summary() },
      "GET /api/sessions/WS-1/ticket": { body: ticket() },
      "POST /api/sessions/WS-1/ticket/print": {
        body: {
          ticketId: "TKT-1",
          printedAt: "2026-10-26T07:49:00Z",
          reprint: false,
          ticket: ticket(),
        },
      },
    });
    render(<DoneScreen session={completed} onSessionChange={vi.fn()} onNextBatch={vi.fn()} />);

    await screen.findByTestId("ticket");
    await userEvent.click(screen.getByRole("button", { name: /Print ticket/ }));

    expect(await screen.findByText("Ticket printed · TKT-1")).toBeInTheDocument();
    expect(screen.queryByText("*** REPRINT ***")).not.toBeInTheDocument();
  });

  it("explains a printer failure in plain words", async () => {
    stubApi({
      "GET /api/sessions/WS-1/summary": { body: summary() },
      "GET /api/sessions/WS-1/ticket": { body: ticket() },
      "POST /api/sessions/WS-1/ticket/print": apiError(503, "PRINTER_UNAVAILABLE"),
    });
    render(<DoneScreen session={completed} onSessionChange={vi.fn()} onNextBatch={vi.fn()} />);

    await screen.findByTestId("ticket");
    await userEvent.click(screen.getByRole("button", { name: /Print ticket/ }));

    expect(
      await screen.findByText("Printer not available. Check the printer and try again."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Print ticket/ })).toBeEnabled();
  });

  it("supports F1 (print) and F3 (next batch)", async () => {
    const { calls } = stubApi({
      "GET /api/sessions/WS-1/summary": { body: summary() },
      "GET /api/sessions/WS-1/ticket": { body: ticket() },
      "POST /api/sessions/WS-1/ticket/print": {
        body: { ticketId: "TKT-2", printedAt: "x", reprint: false, ticket: ticket() },
      },
    });
    const onNextBatch = vi.fn();
    render(<DoneScreen session={completed} onSessionChange={vi.fn()} onNextBatch={onNextBatch} />);
    await screen.findByTestId("ticket");

    await userEvent.keyboard("{F1}");
    await waitFor(() => expect(calls).toContain("POST /api/sessions/WS-1/ticket/print"));
    await userEvent.keyboard("{F3}");
    expect(onNextBatch).toHaveBeenCalled();
  });
});
