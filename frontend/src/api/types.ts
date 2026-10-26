import type { components } from "./schema";

type Schemas = components["schemas"];

export type BatchQueue = Schemas["BatchQueueOut"];
export type Batch = Schemas["BatchOut"];
export type Recipe = Schemas["RecipeOut"];
export type RecipeComponent = Schemas["ComponentOut"];
export type Quantity = Schemas["QuantityOut"];
export type Tolerance = Schemas["ToleranceOut"];
export type DeviceStatus = Schemas["DeviceStatusOut"];
export type Device = Schemas["DeviceOut"];
export type ScanBatch = Schemas["ScanBatchOut"];
export type Availability = Schemas["AvailabilityOut"];
export type Operator = Schemas["OperatorOut"];
export type Session = Schemas["SessionOut"];
export type SessionComponent = Schemas["SessionComponentOut"];
export type ActiveContext = Schemas["ActiveOut"];
export type Live = Schemas["LiveOut"];
export type Summary = Schemas["SummaryOut"];
export type WeighingRecord = Schemas["RecordOut"];
export type Ticket = Schemas["TicketOut"];
export type PrintResult = Schemas["PrintOut"];

export type SimulationProfile = "dispense" | "overshoot" | "below" | "exact";
export type SimulationKind = "dispense" | "overshoot" | "below";
