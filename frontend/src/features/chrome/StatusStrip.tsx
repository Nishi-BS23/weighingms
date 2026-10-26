import { useEffect, useState } from "react";
import type { Device, DeviceStatus } from "../../api/types";
import { formatHm, formatHms } from "../../shared/time";

const DOT: Record<Device["state"], string> = { UP: "up", DOWN: "down", DEGRADED: "degraded" };

function itemText(device: Device, lastContact: string | null | undefined): string {
  if (device.device === "orgatex") {
    return device.state === "UP" && lastContact
      ? `${device.label} · LINKED ${formatHm(lastContact)}`
      : `${device.label} · ${device.text}`;
  }
  if ((device.device === "scanner" || device.device === "printer") && device.state === "UP") {
    return device.label;
  }
  return `${device.label} · ${device.text}`;
}

function Clock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
  return <span className="stat">{formatHms(now)}</span>;
}

interface Props {
  status: DeviceStatus | undefined;
}

export function StatusStrip({ status }: Props) {
  return (
    <div className="strip" data-testid="status-strip">
      {status ? (
        status.devices.map((d) => (
          <span key={d.device} className="stat" data-state={d.state} data-device={d.device}>
            <span className={`dot ${DOT[d.state]}`} />
            {itemText(d, status.orgatexLastContact)}
          </span>
        ))
      ) : (
        <span className="stat">DEVICE STATUS UNKNOWN</span>
      )}
      <span className="spacer" />
      <span className="stat">{status?.language ?? "EN"}</span>
      <Clock />
    </div>
  );
}
