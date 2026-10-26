import type {
  Batch,
  BatchQueue,
  DeviceStatus,
  Live,
  Recipe,
  Session,
  SessionComponent,
  Summary,
  Ticket,
} from "./api/types";

/** API-shaped fixtures for component tests (the running app gets its data from the API). */

export const batch = (overrides: Partial<Batch> = {}): Batch => ({
  batchId: "B-24187",
  orderRef: "SO-9931",
  machineRef: "JET-04",
  fabricDesc: "100% CTN knit",
  fabricWeightKg: "480",
  fabricLot: "100% CTN knit · 480 kg",
  shadeCode: "Teal 4C",
  recipeId: "R-TEAL4C-480",
  componentCount: 5,
  status: "QUEUED",
  selectable: true,
  notSelectableReason: null,
  releasedAt: "2026-10-26T00:12:00Z",
  ...overrides,
});

export const queue = (batches: Batch[]): BatchQueue => ({
  receivedAt: "2026-10-26T06:12:00Z",
  batches,
});

export const recipe = (batchId = "B-24187"): Recipe => ({
  recipeId: "R-TEAL4C-480",
  batchId,
  shadeCode: "Teal 4C",
  version: "3",
  components: [
    {
      componentId: `${batchId}-03`,
      sequence: 3,
      dyestuffCode: "DYE-4471",
      name: "Remazol Yellow RGB",
      shortName: "Yellow RGB",
      colourHex: "#d9a520",
      target: { value: "94.0", unit: "g" },
      tolerance: {
        plusMinus: { value: "0.5", unit: "g" },
        minimum: { value: "93.5", unit: "g" },
        maximum: { value: "94.5", unit: "g" },
        source: "RECIPE",
      },
      scale: { scaleId: "scale-3kg", scaleClass: "PRECISION", label: "3 kg precision" },
      lotId: "2026-0387",
    },
  ],
});

export const deviceStatus = (overrides: Partial<DeviceStatus> = {}): DeviceStatus => ({
  checkedAt: "2026-10-26T07:47:03Z",
  stationName: "STATION 01",
  language: "EN",
  orgatexLastContact: "2026-10-26T07:41:00Z",
  devices: [
    { device: "scale-3kg", label: "SCALE 3 kg", state: "UP", text: "READY" },
    { device: "scale-32kg", label: "SCALE 32 kg", state: "UP", text: "READY" },
    { device: "scanner", label: "SCANNER", state: "UP", text: "READY" },
    { device: "printer", label: "PRINTER", state: "UP", text: "READY" },
    { device: "orgatex", label: "ORGATEX", state: "UP", text: "LINKED" },
  ],
  ...overrides,
});

const q = (value: string, unit: "g" | "kg" = "g") => ({ value, unit });

export const sessionComponent = (overrides: Partial<SessionComponent> = {}): SessionComponent => ({
  componentId: "B-24187-03",
  sequence: 3,
  dyestuffCode: "DYE-4471",
  name: "Remazol Yellow RGB",
  shortName: "Yellow RGB",
  colourHex: "#d9a520",
  target: q("94.0"),
  tolerance: {
    plusMinus: q("0.5"),
    minimum: q("93.5"),
    maximum: q("94.5"),
    source: "RECIPE",
  },
  scale: { scaleId: "scale-3kg", scaleClass: "PRECISION", label: "3 kg precision" },
  lotId: "2026-0387",
  state: "ACTIVE",
  actual: null,
  ...overrides,
});

export const session = (overrides: Partial<Session> = {}): Session => ({
  sessionId: "WS-1",
  batchId: "B-24187",
  orderRef: "SO-9931",
  machineRef: "JET-04",
  shadeCode: "Teal 4C",
  recipeId: "R-TEAL4C-480",
  status: "IN_PROGRESS",
  startedAt: "2026-10-26T07:40:00Z",
  completedAt: null,
  syncStatus: "NOT_SYNCED",
  syncedAt: null,
  progress: { done: 2, total: 3 },
  activeComponentId: "B-24187-03",
  active: {
    componentId: "B-24187-03",
    containerId: "C-12",
    tare: q("214.0"),
    displayMax: q("125.0"),
  },
  components: [
    sessionComponent({
      componentId: "B-24187-01",
      sequence: 1,
      name: "Remazol Brill. Blue RSPL",
      dyestuffCode: "DYE-1180",
      target: q("1240.0"),
      state: "DONE",
      actual: q("1241.5"),
    }),
    sessionComponent({
      componentId: "B-24187-02",
      sequence: 2,
      name: "Remazol Red RB",
      dyestuffCode: "DYE-2204",
      target: q("386.0"),
      state: "DONE",
      actual: q("385.4"),
    }),
    sessionComponent(),
    sessionComponent({
      componentId: "B-24187-04",
      sequence: 4,
      name: "Sodium Sulphate",
      dyestuffCode: "AUX-0101",
      target: q("24.000", "kg"),
      scale: { scaleId: "scale-32kg", scaleClass: "FLOOR", label: "32 kg floor" },
      state: "PENDING",
    }),
  ],
  ...overrides,
});

export const live = (overrides: Partial<Live> = {}): Live => ({
  sessionId: "WS-1",
  componentId: "B-24187-03",
  scaleId: "scale-3kg",
  zone: "WITHIN",
  net: q("94.2"),
  remaining: q("0.0"),
  surplus: null,
  surplusPct: null,
  canConfirm: true,
  scaleAvailable: true,
  calibrationValid: true,
  stable: true,
  statusText: "WITHIN TOLERANCE — PRESS OK TO CONFIRM",
  allowedActions: ["CONFIRM", "RETARE", "QUIT"],
  guidance: null,
  ...overrides,
});

export const summary = (overrides: Partial<Summary> = {}): Summary => ({
  sessionId: "WS-1",
  batchId: "B-24187",
  orderRef: "SO-9931",
  machineRef: "JET-04",
  shadeCode: "Teal 4C",
  completed: true,
  completedAt: "2026-10-26T07:48:22Z",
  componentsWeighed: { done: 5, total: 5 },
  allWithinTolerance: true,
  overriddenCount: 0,
  totalDispensed: q("35.322", "kg"),
  elapsedSeconds: 401,
  elapsedText: "6 min 41 s",
  operatorName: "R. Karim",
  writeBack: { status: "SYNCED", at: "2026-10-26T07:48:22Z", consumptionId: "CNS-1" },
  results: [
    {
      componentId: "B-24187-01",
      sequence: 1,
      name: "Remazol Brill. Blue RSPL",
      shortName: "Blue RSPL",
      target: q("1240.0"),
      actual: q("1241.5"),
      result: "IN_TOLERANCE",
    },
    {
      componentId: "B-24187-05",
      sequence: 5,
      name: "Soda Ash",
      shortName: "Soda Ash",
      target: q("9.600", "kg"),
      actual: q("9.621", "kg"),
      result: "IN_TOLERANCE",
    },
  ],
  ...overrides,
});

export const ticket = (overrides: Partial<Ticket> = {}): Ticket => ({
  header: "FCI DYEING — WEIGHING TICKET",
  batchId: "B-24187",
  orderRef: "SO-9931",
  machineRef: "JET-04",
  shadeCode: "Teal 4C",
  date: "2026-08-04 07:48",
  operatorName: "R. Karim",
  lines: [
    { shortName: "Blue RSPL", target: q("1240.0"), actual: q("1241.5"), overridden: false },
    {
      shortName: "Soda Ash",
      target: q("9.600", "kg"),
      actual: q("9.621", "kg"),
      overridden: false,
    },
  ],
  resultLine: "ALL WITHIN TOLERANCE",
  barcodeValue: "B-24187",
  reprint: false,
  text: [],
  ...overrides,
});
