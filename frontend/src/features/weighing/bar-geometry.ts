/** Progress-bar geometry (display only — no business rules; zones come from the API). */

export interface BarGeometry {
  fillPct: number;
  bandLeftPct: number;
  bandWidthPct: number;
  targetPct: number;
}

const MIN_BAND_WIDTH_PCT = 0.6;

export function barGeometry(
  net: string | null,
  minimum: string,
  maximum: string,
  target: string,
  displayMax: string,
): BarGeometry {
  const full = Number(displayMax);
  const pct = (value: string) => Math.min(100, Math.max(0, (Number(value) / full) * 100));
  const left = pct(minimum);
  return {
    fillPct: net === null ? 0 : pct(net),
    bandLeftPct: left,
    bandWidthPct: Math.max(MIN_BAND_WIDTH_PCT, pct(maximum) - left),
    targetPct: pct(target),
  };
}
