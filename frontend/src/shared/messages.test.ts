import { describe, expect, it } from "vitest";
import { ApiError } from "../api/client";
import { KNOWN_CODES, plainMessage } from "./messages";

/** Every error code the WeighingMS API can return (grep `code = "` in src/weighingms + handlers). */
const API_CODES = [
  "BATCH_NOT_FOUND",
  "BATCH_NOT_SELECTABLE",
  "BATCH_INCOMPLETE",
  "COMPONENT_ALREADY_DONE",
  "COMPONENT_NOT_FOUND",
  "DOMAIN_ERROR",
  "HTTP_ERROR",
  "NOT_FOUND",
  "INTERNAL_ERROR",
  "NO_ACTIVE_COMPONENT",
  "OPERATOR_NOT_FOUND",
  "ORGATEX_BAD_DATA",
  "ORGATEX_UNAVAILABLE",
  "OUT_OF_TOLERANCE",
  "OVERRIDE_NOT_AUTHORISED",
  "OVERRIDE_NOT_NEEDED",
  "PRINTER_UNAVAILABLE",
  "SCALE_CALIBRATION_EXPIRED",
  "SCALE_UNAVAILABLE",
  "SCANNER_UNAVAILABLE",
  "SESSION_COMPLETED",
  "SESSION_NOT_COMPLETED",
  "SESSION_NOT_FOUND",
  "TRAINING_CONTROL_UNAVAILABLE",
  "VALIDATION_ERROR",
];

describe("plainMessage", () => {
  it("has an operator message for every API error code", () => {
    expect(API_CODES.filter((code) => !KNOWN_CODES.includes(code))).toEqual([]);
  });

  it("never shows codes, JSON or stack traces to operators", () => {
    for (const code of [...API_CODES, "NETWORK_ERROR", "BAD_RESPONSE"]) {
      const text = plainMessage(new ApiError(500, code, "Traceback (most recent call last)"));
      if (code === "OUT_OF_TOLERANCE" || code.startsWith("BATCH_")) continue; // server text is plain
      expect(text).not.toMatch(/[A-Z]+_[A-Z_]+|Traceback|{|}/);
    }
  });

  it("uses the specific server wording where it is already plain", () => {
    const error = new ApiError(
      409,
      "OUT_OF_TOLERANCE",
      "Soda Ash: 9.500 kg is outside 9.552 – 9.648 kg.",
    );

    expect(plainMessage(error)).toBe("Soda Ash: 9.500 kg is outside 9.552 – 9.648 kg.");
  });

  it("falls back to a generic sentence for unexpected errors", () => {
    expect(plainMessage(new Error("boom"))).toBe("Something went wrong. Try again.");
  });
});
