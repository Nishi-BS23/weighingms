const pad = (n: number) => String(n).padStart(2, "0");

/** "HH:MM" in the station's local time. */
export function formatHm(iso: string | Date): string {
  const d = typeof iso === "string" ? new Date(iso) : iso;
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

/** "HH:MM:SS" in the station's local time. */
export function formatHms(iso: string | Date): string {
  const d = typeof iso === "string" ? new Date(iso) : iso;
  return `${formatHm(d)}:${pad(d.getSeconds())}`;
}
