const API_PREFIX = "/api/v1";

export const endpoints = {
  auth: {
    register: `${API_PREFIX}/auth/register`,
    login: `${API_PREFIX}/auth/login`,
    logout: `${API_PREFIX}/auth/logout`,
    me: `${API_PREFIX}/auth/me`,
  },
  goals: {
    active: `${API_PREFIX}/goals/active`,
    collection: `${API_PREFIX}/goals`,
    item: (goalId: string) => `${API_PREFIX}/goals/${goalId}`,
  },
  financialProfile: `${API_PREFIX}/financial-profile`,
  incomeSources: {
    collection: `${API_PREFIX}/income-sources`,
    item: (incomeSourceId: string) => `${API_PREFIX}/income-sources/${incomeSourceId}`,
  },
  plannedExpenses: {
    collection: `${API_PREFIX}/planned-expenses`,
    item: (plannedExpenseId: string) => `${API_PREFIX}/planned-expenses/${plannedExpenseId}`,
  },
  dashboard: `${API_PREFIX}/dashboard`,
  calculationSnapshots: {
    latest: `${API_PREFIX}/calculation-snapshots/latest`,
  },
} as const;
