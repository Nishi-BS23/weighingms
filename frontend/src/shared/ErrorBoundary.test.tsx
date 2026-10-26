import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ErrorBoundary } from "./ErrorBoundary";

function Broken(): never {
  throw new Error("render failure");
}

describe("ErrorBoundary", () => {
  it("replaces a broken screen with a plain message and a way back", async () => {
    vi.spyOn(console, "error").mockImplementation(() => undefined); // React logs caught errors
    const onBack = vi.fn();
    render(
      <ErrorBoundary onBack={onBack}>
        <Broken />
      </ErrorBoundary>,
    );

    expect(screen.getByText("Something went wrong on this screen.")).toBeInTheDocument();
    expect(screen.queryByText("render failure")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Back to batch queue" }));
    expect(onBack).toHaveBeenCalled();
  });
});
