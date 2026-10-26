import type {
  Availability,
  Batch,
  BatchQueue,
  DeviceStatus,
  Live,
  Operator,
  Quantity,
  Recipe,
  PrintResult,
  ScanBatch,
  Session,
  SimulationKind,
  SimulationProfile,
  Summary,
  Ticket,
} from "./types";

/** An error from the WeighingMS API, carrying the stable code from the standard error body. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly details: Record<string, unknown> = {},
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface ErrorBody {
  error: { code: string; message: string; details?: Record<string, unknown> };
}

function isErrorBody(value: unknown): value is ErrorBody {
  if (typeof value !== "object" || value === null || !("error" in value)) return false;
  const error = value.error;
  return typeof error === "object" && error !== null && "code" in error && "message" in error;
}

async function request<T>(
  method: "GET" | "POST" | "PUT",
  path: string,
  body?: unknown,
  signal?: AbortSignal,
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      method,
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(0, "NETWORK_ERROR", "The station service is not reachable.");
  }
  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      throw new ApiError(
        response.status,
        "BAD_RESPONSE",
        "The station service sent an invalid reply.",
      );
    }
  }
  if (!response.ok) {
    if (isErrorBody(data)) {
      throw new ApiError(response.status, data.error.code, data.error.message, data.error.details);
    }
    throw new ApiError(response.status, `HTTP_${response.status}`, "The request failed.");
  }
  return data as T;
}

const id = encodeURIComponent;

export const api = {
  batches: (signal?: AbortSignal) => request<BatchQueue>("GET", "/api/batches", undefined, signal),
  batch: (batchId: string) => request<Batch>("GET", `/api/batches/${id(batchId)}`),
  recipe: (batchId: string) => request<Recipe>("GET", `/api/batches/${id(batchId)}/recipe`),
  deviceStatus: (signal?: AbortSignal) =>
    request<DeviceStatus>("GET", "/api/devices/status", undefined, signal),
  scans: (after: number, signal?: AbortSignal) =>
    request<ScanBatch>("GET", `/api/scanner/scans?after=${after}`, undefined, signal),
  currentOperator: () => request<Operator>("GET", "/api/operators/current"),
  signIn: (badgeId: string) => request<Operator>("POST", "/api/operators/sign-in", { badgeId }),
  startSession: (batchId: string) => request<Session>("POST", "/api/sessions", { batchId }),
  session: (sessionId: string) => request<Session>("GET", `/api/sessions/${id(sessionId)}`),
  activate: (sessionId: string, componentId: string) =>
    request<Session>(
      "POST",
      `/api/sessions/${id(sessionId)}/components/${id(componentId)}/activate`,
    ),
  live: (sessionId: string, signal?: AbortSignal) =>
    request<Live>("GET", `/api/sessions/${id(sessionId)}/live`, undefined, signal),
  retare: (sessionId: string) => request<Live>("POST", `/api/sessions/${id(sessionId)}/retare`),
  confirm: (sessionId: string) =>
    request<Session>("POST", `/api/sessions/${id(sessionId)}/confirm`),
  override: (sessionId: string, supervisorPin: string, reason: string) =>
    request<Session>("POST", `/api/sessions/${id(sessionId)}/override`, { supervisorPin, reason }),
  quit: (sessionId: string) => request<Session>("POST", `/api/sessions/${id(sessionId)}/quit`),
  sync: (sessionId: string) => request<Session>("POST", `/api/sessions/${id(sessionId)}/sync`),
  summary: (sessionId: string) => request<Summary>("GET", `/api/sessions/${id(sessionId)}/summary`),
  ticket: (sessionId: string) => request<Ticket>("GET", `/api/sessions/${id(sessionId)}/ticket`),
  printTicket: (sessionId: string) =>
    request<PrintResult>("POST", `/api/sessions/${id(sessionId)}/ticket/print`),
  training: {
    scan: (code: string) => request<unknown>("POST", "/api/training/scan", { code }),
    availability: () => request<Availability>("GET", "/api/training/availability"),
    setAvailability: (system: string, available: boolean) =>
      request<Availability>("PUT", `/api/training/availability/${id(system)}`, { available }),
    reset: () => request<unknown>("POST", "/api/training/reset"),
    simulate: (scaleId: string, profile: SimulationProfile, net: Quantity) =>
      request<unknown>("POST", `/api/training/scales/${id(scaleId)}/simulate`, { profile, net }),
    simulateActive: (sessionId: string, kind: SimulationKind) =>
      request<unknown>("POST", "/api/training/simulate", { sessionId, kind }),
    resetWeighing: (sessionId: string) =>
      request<unknown>("POST", "/api/training/reset-weighing", { sessionId }),
  },
};
