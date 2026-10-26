import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { StepIndicator } from "./StepIndicator";

describe("StepIndicator", () => {
  it("highlights the current step and blocks unreachable steps", async () => {
    const onSelect = vi.fn();
    render(
      <StepIndicator
        current="weigh"
        reachable={{ queue: true, weigh: true, done: false }}
        onSelect={onSelect}
      />,
    );

    expect(screen.getByRole("button", { name: "2 · Weigh" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("button", { name: "3 · Confirm & print" })).toBeDisabled();

    await userEvent.click(screen.getByRole("button", { name: "1 · Select batch" }));
    expect(onSelect).toHaveBeenCalledWith("queue");
  });
});
