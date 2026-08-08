import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppShell } from "../components/layout/AppShell.tsx";
import { RequireAuth } from "../features/auth/RequireAuth.tsx";
import { PlaceholderRoute } from "../routes/app/PlaceholderRoute.tsx";
import { LoginRoute } from "../routes/auth/LoginRoute.tsx";
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
        element: (
          <PlaceholderRoute
            title="Dashboard"
            description="This route will render backend-owned safe-to-spend, pace status, shortfall, and snapshot data."
          />
        ),
      },
      {
        path: routes.goal,
        element: (
          <PlaceholderRoute
            title="Goal setup"
            description="This route will manage the one active savings goal supported by the MVP."
          />
        ),
      },
      {
        path: routes.financialInputs,
        element: (
          <PlaceholderRoute
            title="Financial inputs"
            description="This route will manage manual cash, reserve, income, and planned expense assumptions."
          />
        ),
      },
      {
        path: routes.calculation,
        element: (
          <PlaceholderRoute
            title="Calculation details"
            description="This route will explain the latest deterministic pace-v1 result and immutable snapshot."
          />
        ),
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to={routes.landing} replace />,
  },
]);
