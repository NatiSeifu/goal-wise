import { describe, expect, it } from "vitest";

import { toApiError } from "./errors.ts";

describe("API error normalization", () => {
  it("uses backend error payload details when present", () => {
    const error = toApiError(422, {
      error: {
        code: "validation_error",
        fields: {
          next_date: ["Date must not be in the past."],
        },
        message: "Request validation failed.",
      },
    });

    expect(error.status).toBe(422);
    expect(error.code).toBe("validation_error");
    expect(error.message).toBe("Request validation failed.");
    expect(error.fields).toEqual({
      next_date: ["Date must not be in the past."],
    });
  });

  it("falls back to a generic request error for non-standard payloads", () => {
    const error = toApiError(500, { detail: "Internal Server Error" });

    expect(error.status).toBe(500);
    expect(error.code).toBe("request_failed");
    expect(error.message).toBe("Request failed. Please try again.");
    expect(error.fields).toBeNull();
  });
});
