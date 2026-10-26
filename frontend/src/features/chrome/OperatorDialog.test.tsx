import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { apiError, stubApi } from "../../test-utils";
import { OperatorDialog } from "./OperatorDialog";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("OperatorDialog", () => {
  it("signs in by badge", async () => {
    const operator = {
      operatorId: "OP-1002",
      name: "M. Hossain",
      shift: "Shift B",
      role: "OPERATOR",
    };
    stubApi({ "POST /api/operators/sign-in": { body: operator } });
    const onSignedIn = vi.fn();
    render(<OperatorDialog onSignedIn={onSignedIn} onCancel={vi.fn()} />);

    await userEvent.type(screen.getByLabelText("Badge"), "1002");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => expect(onSignedIn).toHaveBeenCalledWith(operator));
  });

  it("explains an unknown badge and cancels with Escape", async () => {
    stubApi({ "POST /api/operators/sign-in": apiError(404, "OPERATOR_NOT_FOUND") });
    const onCancel = vi.fn();
    render(<OperatorDialog onSignedIn={vi.fn()} onCancel={onCancel} />);

    await userEvent.type(screen.getByLabelText("Badge"), "0000{Enter}");
    expect(
      await screen.findByText("This badge is not registered at the station."),
    ).toBeInTheDocument();

    await userEvent.keyboard("{Escape}");
    expect(onCancel).toHaveBeenCalled();
  });
});
