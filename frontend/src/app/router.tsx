import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppShell } from "../components/layout/AppShell.tsx";
import { RequireAuth } from "../features/auth/RequireAuth.tsx";
import { LoginRoute } from "../routes/auth/LoginRoute.tsx";
import { CalculationRoute } from "../routes/calculation/CalculationRoute.tsx";
import { DashboardRoute } from "../routes/dashboard/DashboardRoute.tsx";
import { FinancialInputsRoute } from "../routes/financial-inputs/FinancialInputsRoute.tsx";
import { GoalRoute } from "../routes/goal/GoalRoute.tsx";
import { RegisterRoute } from "../routes/auth/RegisterRoute.tsx";
import { LandingRoute } from "../routes/landing/LandingRoute.tsx";
import { routes } from "./routes.ts";

export const router = createBrowserRouter([
  {
    path: routes.landing,
    element: <LandingRoute />,
  },
  {
    path: routes.login,
    element: <LoginRoute />,
  },
  {
    path: routes.register,
    element: <RegisterRoute />,
  },
  {
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      {
        path: routes.dashboard,
        element: <DashboardRoute />,
      },
      {
        path: routes.goal,
        element: <GoalRoute />,
      },
      {
        path: routes.financialInputs,
        element: <FinancialInputsRoute />,
      },
      {
        path: routes.calculation,
        element: <CalculationRoute />,
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to={routes.landing} replace />,
  },
]);
