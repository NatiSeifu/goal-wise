import { describe, expect, it } from "vitest";

import {
  centsToDollarInput,
  dollarInputToCents,
  formatCents,
  formatDate,
  formatPercent,
} from "./format.ts";

describe("format utilities", () => {
  it("formats integer cents as whole-dollar display currency", () => {
    expect(formatCents(123456)).toBe("$1,235");
  });

  it("converts integer cents to fixed dollar input values", () => {
    expect(centsToDollarInput(123456)).toBe("1234.56");
  });

  it("converts dollar input values to integer cents", () => {
    expect(dollarInputToCents("1234.56")).toBe(123456);
  });

  it("treats blank dollar input as zero cents", () => {
    expect(dollarInputToCents("  ")).toBe(0);
  });

  it("formats ISO date-only values without time zone shifting the day", () => {
    expect(formatDate("2026-08-13")).toBe("Aug 13, 2026");
  });

  it("formats percentages without decimal places", () => {
    expect(formatPercent(42.49)).toBe("42%");
  });
});
