import { describe, expect, it } from "vitest";

import {
  classificationLabel,
  confidenceLabel,
  formatInputCategoryList,
  frequencyLabel,
  humanizeTechnicalKey,
  inputCategoryLabel,
} from "./labels.ts";

describe("label utilities", () => {
  it("maps backend input category keys to user-facing labels", () => {
    expect(inputCategoryLabel("goal")).toBe("Goal details");
    expect(inputCategoryLabel("financial_profile")).toBe("Financial profile");
    expect(inputCategoryLabel("income_sources")).toBe("Income sources");
    expect(inputCategoryLabel("planned_expenses")).toBe("Planned expenses");
    expect(inputCategoryLabel("transactions")).toBe("Transactions");
  });

  it("humanizes unknown backend keys without exposing underscores", () => {
    expect(inputCategoryLabel("future_budget_items")).toBe("Future Budget Items");
  });

  it("humanizes technical keys for audit details", () => {
    expect(humanizeTechnicalKey("goal_updated")).toBe("Goal Updated");
  });

  it("formats changed input categories as a readable list", () => {
    expect(formatInputCategoryList(["goal", "planned_expenses"])).toBe(
      "Goal details, Planned expenses",
    );
  });

  it("maps planning values to user-facing labels", () => {
    expect(frequencyLabel("one_time")).toBe("One time");
    expect(frequencyLabel("biweekly")).toBe("Every two weeks");
    expect(confidenceLabel("unconfirmed")).toBe("Not confirmed");
    expect(classificationLabel("discretionary")).toBe("Discretionary");
  });

  it("humanizes unknown planning values without exposing internal formatting", () => {
    expect(frequencyLabel("every_other_month")).toBe("Every Other Month");
    expect(confidenceLabel(null)).toBe("Not specified");
    expect(classificationLabel(null)).toBe("Not specified");
  });
});
