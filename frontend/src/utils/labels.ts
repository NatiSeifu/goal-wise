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

const paceStatusLabels: Record<string, string> = {
  ahead: "Ahead of pace",
  "at risk": "At risk",
  at_risk: "At risk",
  completed: "Completed",
  "off pace": "Needs attention",
  off_pace: "Needs attention",
  "on track": "On track",
  on_track: "On track",
};

const paceStatusDescriptions: Record<string, string> = {
  ahead: "You are saving faster than your goal requires.",
  "at risk": "Your savings pace may need attention to meet the goal.",
  at_risk: "Your savings pace may need attention to meet the goal.",
  completed: "You have reached your savings goal.",
  "off pace": "Your current savings pace is below what the goal requires.",
  off_pace: "Your current savings pace is below what the goal requires.",
  "on track": "Your current plan is keeping the goal on schedule.",
  on_track: "Your current plan is keeping the goal on schedule.",
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

export function paceStatusLabel(value: string) {
  return paceStatusLabels[value.toLowerCase()] ?? humanizeTechnicalKey(value);
}

export function paceStatusDescription(value: string) {
  return paceStatusDescriptions[value.toLowerCase()] ?? "Review your current plan against the goal timeline.";
}
