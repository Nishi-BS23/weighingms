import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { live, session, sessionComponent } from "../../test-fixtures";
import { Readout, SurplusPanel, ToleranceBar, WeighHeader } from "./WeighingPanel";

const component = sessionComponent();
const active = session().active!;

describe("Weighing panel", () => {
  it("shows identity, lot, container, tare and the automatic scale", () => {
    render(<WeighHeader component={component} active={active} />);

    expect(screen.getByText("Remazol Yellow RGB")).toBeInTheDocument();
    expect(
      screen.getByText("DYE-4471 · LOT 2026-0387 · CONTAINER C-12 · TARE 214.0 g"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("scale-selected")).toHaveTextContent("3 kg precision");
    expect(screen.getByText("automatic")).toBeInTheDocument();
  });

  it("renders the live readout with the zone from the API", () => {
    render(
      <Readout
        component={component}
        live={live({
          zone: "NEAR",
          net: { value: "93.4", unit: "g" },
          remaining: { value: "0.6", unit: "g" },
        })}
      />,
    );

    expect(screen.getByTestId("weighed-now")).toHaveTextContent("93.4");
    expect(screen.getByTestId("still-to-weigh")).toHaveTextContent("0.6");
    expect(screen.getByTestId("weighed-now").closest(".cell")).toHaveAttribute("data-zone", "NEAR");
  });

  it("shows a dash when the scale is offline", () => {
    render(<Readout component={component} live={live({ zone: "OFFLINE", net: null })} />);

    expect(screen.getByTestId("weighed-now")).toHaveTextContent("—");
  });

  it("captions the tolerance band and shows the status text", () => {
    render(
      <ToleranceBar
        component={component}
        active={active}
        live={live()}
        overrideRequested={false}
      />,
    );

    expect(screen.getByTestId("tolerance-caption")).toHaveTextContent(
      "TOLERANCE ±0.5 g (93.5 – 94.5)",
    );
    expect(screen.getByTestId("status-line")).toHaveTextContent(
      "WITHIN TOLERANCE — PRESS OK TO CONFIRM",
    );
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "75");
    expect(screen.getByText("125.0 g")).toBeInTheDocument();
  });

  it("shows the override request in the status line", () => {
    render(<ToleranceBar component={component} active={active} live={live()} overrideRequested />);

    expect(screen.getByTestId("status-line")).toHaveTextContent(
      "OVERRIDE REQUESTED — AWAITING SUPERVISOR",
    );
  });

  it("shows the surplus panel with guidance only when over tolerance", () => {
    const over = live({
      zone: "OVER",
      surplus: { value: "2.4", unit: "g" },
      surplusPct: "2.6",
      guidance: "Remove material until the weight is back within 93.5 – 94.5 g.",
    });
    const { rerender } = render(<SurplusPanel live={over} unit="g" />);

    expect(screen.getByText("Surplus +2.4 g (+2.6%) — over tolerance")).toBeInTheDocument();
    expect(screen.getByText(/back within 93.5 – 94.5 g/)).toBeInTheDocument();

    rerender(<SurplusPanel live={live()} unit="g" />);
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
