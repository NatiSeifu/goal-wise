export const routes = {
  landing: "/",
  login: "/login",
  register: "/register",
  dashboard: "/dashboard",
  goal: "/goal",
  financialInputs: "/financial-inputs",
  calculation: "/calculation",
} as const;

export type AppRoute = (typeof routes)[keyof typeof routes];
