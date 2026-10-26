/**
 * Bars for the ticket preview, derived deterministically from the barcode value. This is a visual
 * stand-in only: the real printer renders the agreed symbology (UQ-11).
 */
export interface Bar {
  width: number;
  gap: boolean;
}

export function barcodeBars(value: string): Bar[] {
  const bars: Bar[] = [];
  for (const [i, char] of [...value].entries()) {
    const code = char.charCodeAt(0);
    bars.push({ width: 1 + (code % 3), gap: false });
    bars.push({ width: 1 + ((code >> 2) % 2), gap: true });
    bars.push({ width: 1 + ((code + i) % 3), gap: false });
    bars.push({ width: 1, gap: true });
  }
  return bars;
}
