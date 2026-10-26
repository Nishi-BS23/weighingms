import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { session } from "../../test-fixtures";
import { RecipeRail } from "./RecipeRail";

describe("RecipeRail", () => {
  it("shows the recipe header and each component's state as in the prototype", () => {
    render(<RecipeRail session={session()} disabled={false} onActivate={vi.fn()} />);

    expect(screen.getByText("Recipe · Teal 4C")).toBeInTheDocument();
    expect(screen.getByText("2 of 3 components weighed")).toBeInTheDocument();
    expect(screen.getByText("✓ 1241.5")).toBeInTheDocument();
    expect(screen.getByText("WEIGHING")).toBeInTheDocument();
    expect(screen.getByText("PENDING")).toBeInTheDocument();
    expect(screen.getByText("DYE-1180 · 3 kg")).toBeInTheDocument();
    expect(screen.getByText("AUX-0101 · 32 kg")).toBeInTheDocument();
  });

  it("activates only pending components", async () => {
    const onActivate = vi.fn();
    render(<RecipeRail session={session()} disabled={false} onActivate={onActivate} />);

    await userEvent.click(screen.getByText("Remazol Brill. Blue RSPL"));
    await userEvent.click(screen.getByText("Remazol Yellow RGB"));
    await userEvent.click(screen.getByText("Sodium Sulphate"));

    expect(onActivate).toHaveBeenCalledTimes(1);
    expect(onActivate).toHaveBeenCalledWith("B-24187-04");
  });

  it("ignores clicks while an action is running", async () => {
    const onActivate = vi.fn();
    render(<RecipeRail session={session()} disabled onActivate={onActivate} />);

    await userEvent.click(screen.getByText("Sodium Sulphate"));

    expect(onActivate).not.toHaveBeenCalled();
  });
});
