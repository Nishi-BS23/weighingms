import { describe, expect, it } from "vitest";
import { barGeometry } from "./bar-geometry";

describe("barGeometry", () => {
  it("places band, target line and fill on the display scale", () => {
    const g = barGeometry("62.5", "93.5", "94.5", "94.0", "125.0");

    expect(g.fillPct).toBeCloseTo(50);
    expect(g.bandLeftPct).toBeCloseTo(74.8);
    expect(g.bandWidthPct).toBeCloseTo(0.8);
    expect(g.targetPct).toBeCloseTo(75.2);
  });

  it("keeps a visible band and clamps the fill", () => {
    const g = barGeometry("500.0", "23.880", "24.120", "24.000", "320.0");

    expect(g.fillPct).toBe(100);
    expect(g.bandWidthPct).toBe(0.6);
  });

  it("shows an empty bar without a reading", () => {
    expect(barGeometry(null, "93.5", "94.5", "94.0", "125.0").fillPct).toBe(0);
  });
});
