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
