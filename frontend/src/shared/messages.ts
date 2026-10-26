import { ApiError } from "../api/client";

/** Plain-language operator messages for API error codes (Brief C-05: limited computer literacy). */
const MESSAGES: Record<string, string> = {
  NETWORK_ERROR: "The station service is not reachable. Wait a moment and try again.",
  ORGATEX_UNAVAILABLE: "OrgaTEX is not reachable. Check the connection and retry.",
  ORGATEX_BAD_DATA: "OrgaTEX sent data the station cannot read. Call your supervisor.",
  BATCH_NOT_FOUND: "This batch is not in the OrgaTEX queue.",
  SCANNER_UNAVAILABLE: "The barcode scanner is not available. Touch a row to select a batch.",
  TRAINING_CONTROL_UNAVAILABLE: "The training simulator is not reachable.",
  BATCH_NOT_SELECTABLE: "This batch cannot be weighed at the moment.",
  SCALE_UNAVAILABLE: "The scale is not responding. Check the connection.",
  SCALE_CALIBRATION_EXPIRED: "The scale's calibration has expired. Call your supervisor.",
  OVERRIDE_NOT_AUTHORISED: "The supervisor PIN was not accepted.",
  OVERRIDE_NOT_NEEDED:
    "No override is needed: the weight is within tolerance or the scale is empty.",
  COMPONENT_ALREADY_DONE: "This component has already been weighed.",
  SESSION_COMPLETED: "This batch is already completed.",
  NO_ACTIVE_COMPONENT: "Select a component to weigh.",
  OPERATOR_NOT_FOUND: "This badge is not registered at the station.",
  BATCH_INCOMPLETE: "The batch cannot be completed until every component is weighed.",
  PRINTER_UNAVAILABLE: "Printer not available. Check the printer and try again.",
  SESSION_NOT_COMPLETED: "The ticket can be printed once every component is weighed.",
  SESSION_NOT_FOUND: "This weighing session no longer exists. Select the batch again.",
  OUT_OF_TOLERANCE: "The weight is outside tolerance and cannot be confirmed.",
  VALIDATION_ERROR: "Some information is missing or not valid. Check and try again.",
  INTERNAL_ERROR: "Something went wrong in the station service. Try again or call your supervisor.",
  BAD_RESPONSE: "The station service sent an invalid reply. Try again.",
  COMPONENT_NOT_FOUND: "This component is not part of the recipe. Select the batch again.",
  NOT_FOUND: "The station could not find what was asked for. Go back and try again.",
  HTTP_ERROR: "The station service could not handle the request. Try again.",
  DOMAIN_ERROR: "The station could not complete this action. Call your supervisor.",
};

/** All codes the operator terminal knows how to explain (used by tests to keep the table complete). */
export const KNOWN_CODES = Object.keys(MESSAGES);

/** Codes whose server message is already plain and more specific than the generic text. */
const USE_SERVER_MESSAGE = new Set([
  "OUT_OF_TOLERANCE",
  "BATCH_NOT_SELECTABLE",
  "BATCH_INCOMPLETE",
]);

export function plainMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (USE_SERVER_MESSAGE.has(error.code)) return error.message;
    return MESSAGES[error.code] ?? error.message;
  }
  return "Something went wrong. Try again.";
}

export function errorCode(error: unknown): string | undefined {
  return error instanceof ApiError ? error.code : undefined;
}
