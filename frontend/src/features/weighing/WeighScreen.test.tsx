import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { live, session } from "../../test-fixtures";
import { apiError, stubApi } from "../../test-utils";
import { WeighScreen } from "./WeighScreen";

afterEach(() => {
  vi.unstubAllGlobals();
});

const confirmButton = () => screen.getByRole("button", { name: /OK · Confirm/ });

describe("WeighScreen", () => {
  it("enables Confirm only when the API says the weight can be confirmed", async () => {
    let reading = live({
      zone: "NEAR",
      canConfirm: false,
      statusText: "DISPENSE — 0.6 g REMAINING",
    });
    stubApi({ "GET /api/sessions/WS-1/live": () => ({ body: reading }) });
    render(<WeighScreen session={session()} onSessionChange={vi.fn()} onQuit={vi.fn()} />);

    await screen.findByText("DISPENSE — 0.6 g REMAINING");
    expect(confirmButton()).toBeDisabled();

    reading = live();
    await waitFor(() => expect(confirmButton()).toBeEnabled());
  });

  it("confirms through the API and hands back the updated session", async () => {
    const next = session({ progress: { done: 3, total: 3 }, activeComponentId: "B-24187-04" });
    const { calls } = stubApi({
      "GET /api/sessions/WS-1/live": { body: live() },
      "POST /api/sessions/WS-1/confirm": { body: next },
    });
    const onSessionChange = vi.fn();
    render(<WeighScreen session={session()} onSessionChange={onSessionChange} onQuit={vi.fn()} />);

    await waitFor(() => expect(confirmButton()).toBeEnabled());
    await userEvent.click(confirmButton());

    await waitFor(() => expect(onSessionChange).toHaveBeenCalledWith(next));
    expect(calls).toContain("POST /api/sessions/WS-1/confirm");
  });

  it("shows the server's reason when a confirm is refused", async () => {
    stubApi({
      "GET /api/sessions/WS-1/live": { body: live() },
      "POST /api/sessions/WS-1/confirm": apiError(
        409,
        "OUT_OF_TOLERANCE",
        "Remazol Yellow RGB: 94.6 g is outside 93.5 – 94.5 g.",
      ),
    });
    render(<WeighScreen session={session()} onSessionChange={vi.fn()} onQuit={vi.fn()} />);

    await waitFor(() => expect(confirmButton()).toBeEnabled());
    await userEvent.click(confirmButton());

    expect(
      await screen.findByText("Remazol Yellow RGB: 94.6 g is outside 93.5 – 94.5 g."),
    ).toBeInTheDocument();
  });

  it("re-tares through the API", async () => {
    const { calls } = stubApi({
      "GET /api/sessions/WS-1/live": { body: live() },
      "POST /api/sessions/WS-1/retare": { body: live({ net: { value: "0.0", unit: "g" } }) },
    });
    render(<WeighScreen session={session()} onSessionChange={vi.fn()} onQuit={vi.fn()} />);

    await userEvent.click(screen.getByRole("button", { name: /Re-tare/ }));

    await waitFor(() => expect(calls).toContain("POST /api/sessions/WS-1/retare"));
  });

  it("asks before quitting and returns to the queue", async () => {
    const { calls } = stubApi({
      "GET /api/sessions/WS-1/live": { body: live() },
      "POST /api/sessions/WS-1/quit": { body: session({ activeComponentId: null, active: null }) },
    });
    const onQuit = vi.fn();
    render(<WeighScreen session={session()} onSessionChange={vi.fn()} onQuit={onQuit} />);

    await userEvent.click(screen.getByRole("button", { name: /Quit/ }));
    expect(screen.getByRole("dialog", { name: "Abandon Remazol Yellow RGB?" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Quit" }));

    await waitFor(() => expect(onQuit).toHaveBeenCalled());
    expect(calls).toContain("POST /api/sessions/WS-1/quit");
  });

  it("runs a supervisor override with PIN and reason", async () => {
    let pinOk = false;
    const overridden = session({ progress: { done: 3, total: 3 } });
    const { calls, fetchMock } = stubApi({
      "GET /api/sessions/WS-1/live": {
        body: live({
          zone: "OVER",
          canConfirm: false,
          statusText: "OVER TOLERANCE — SURPLUS +2.4 g",
        }),
      },
      "POST /api/sessions/WS-1/override": () =>
        pinOk ? { body: overridden } : apiError(403, "OVERRIDE_NOT_AUTHORISED"),
    });
    const onSessionChange = vi.fn();
    render(<WeighScreen session={session()} onSessionChange={onSessionChange} onQuit={vi.fn()} />);

    await userEvent.click(screen.getByRole("button", { name: "Supervisor override" }));
    expect(screen.getByTestId("status-line")).toHaveTextContent(
      "OVERRIDE REQUESTED — AWAITING SUPERVISOR",
    );
    await userEvent.type(screen.getByLabelText("Supervisor PIN"), "1111");
    await userEvent.type(screen.getByLabelText("Reason"), "Lab approved");
    await userEvent.click(screen.getByRole("button", { name: "Authorise" }));
    expect(await screen.findByText("The supervisor PIN was not accepted.")).toBeInTheDocument();

    pinOk = true;
    await userEvent.type(screen.getByLabelText("Supervisor PIN"), "2468");
    await userEvent.click(screen.getByRole("button", { name: "Authorise" }));

    await waitFor(() => expect(onSessionChange).toHaveBeenCalledWith(overridden));
    const first = calls.findIndex((c) => c.endsWith("/override"));
    const body = fetchMock.mock.calls[first]?.[1]?.body;
    expect(body).toBe(JSON.stringify({ supervisorPin: "1111", reason: "Lab approved" }));
  });

  it("requires a reason for an override", async () => {
    const { calls } = stubApi({ "GET /api/sessions/WS-1/live": { body: live() } });
    render(<WeighScreen session={session()} onSessionChange={vi.fn()} onQuit={vi.fn()} />);

    await userEvent.click(screen.getByRole("button", { name: "Supervisor override" }));
    await userEvent.type(screen.getByLabelText("Supervisor PIN"), "2468");
    await userEvent.click(screen.getByRole("button", { name: "Authorise" }));

    expect(screen.getByText("Enter the reason for the override.")).toBeInTheDocument();
    expect(calls.some((c) => c.includes("override"))).toBe(false);
  });
});

describe("WeighScreen function keys", () => {
  it("F1 confirms only when allowed, F2 re-tares, F4 opens the quit dialog", async () => {
    let reading = live({ zone: "NEAR", canConfirm: false });
    const { calls } = stubApi({
      "GET /api/sessions/WS-1/live": () => ({ body: reading }),
      "POST /api/sessions/WS-1/confirm": { body: session() },
      "POST /api/sessions/WS-1/retare": { body: live() },
    });
    render(<WeighScreen session={session()} onSessionChange={vi.fn()} onQuit={vi.fn()} />);
    await screen.findByText(reading.statusText);

    await userEvent.keyboard("{F1}");
    expect(calls).not.toContain("POST /api/sessions/WS-1/confirm");

    reading = live();
    await waitFor(() => expect(confirmButton()).toBeEnabled());
    await userEvent.keyboard("{F1}");
    await waitFor(() => expect(calls).toContain("POST /api/sessions/WS-1/confirm"));

    await userEvent.keyboard("{F2}");
    await waitFor(() => expect(calls).toContain("POST /api/sessions/WS-1/retare"));

    await userEvent.keyboard("{F4}");
    expect(screen.getByRole("dialog", { name: "Abandon Remazol Yellow RGB?" })).toBeInTheDocument();
    await userEvent.keyboard("{F1}");
    expect(calls.filter((c) => c === "POST /api/sessions/WS-1/confirm")).toHaveLength(1);
  });
});
