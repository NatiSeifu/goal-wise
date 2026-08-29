const inputCategoryLabels: Record<string, string> = {
  financial_profile: "Financial profile",
  goal: "Goal details",
  income_sources: "Income sources",
  planned_expenses: "Planned expenses",
  transactions: "Transactions",
};

export function inputCategoryLabel(category: string) {
  return inputCategoryLabels[category] ?? humanizeTechnicalKey(category);
}

export function formatInputCategoryList(categories: string[]) {
  return categories.map(inputCategoryLabel).join(", ");
}

export function humanizeTechnicalKey(value: string) {
  return value
    .split("_")
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(" ");
}

const frequencyLabels: Record<string, string> = {
  one_time: "One time",
  weekly: "Every week",
  biweekly: "Every two weeks",
  monthly: "Every month",
};

const confidenceLabels: Record<string, string> = {
  confirmed: "Confirmed",
  unconfirmed: "Not confirmed",
};

const classificationLabels: Record<string, string> = {
  essential: "Essential",
  discretionary: "Discretionary",
};

export function frequencyLabel(value: string) {
  return frequencyLabels[value] ?? humanizeTechnicalKey(value);
}

export function confidenceLabel(value: string | null) {
  return value === null ? "Not specified" : confidenceLabels[value] ?? humanizeTechnicalKey(value);
}

export function classificationLabel(value: string | null) {
  return value === null ? "Not specified" : classificationLabels[value] ?? humanizeTechnicalKey(value);
}
