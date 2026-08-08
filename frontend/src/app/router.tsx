import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppShell } from "../components/layout/AppShell.tsx";
import { PlaceholderRoute } from "../routes/app/PlaceholderRoute.tsx";
import { LandingRoute } from "../routes/landing/LandingRoute.tsx";
import { routes } from "./routes.ts";

export const router = createBrowserRouter([
  {
    path: routes.landing,
    element: <LandingRoute />,
  },
  {
    path: routes.login,
    element: (
      <PlaceholderRoute
        title="Sign in"
        description="The auth screen will connect to the backend session and CSRF flow in the auth slice."
      />
    ),
  },
  {
    path: routes.register,
    element: (
      <PlaceholderRoute
        title="Create account"
        description="Registration will create the account, receive the CSRF token, and enter the protected app."
      />
    ),
  },
  {
    element: <AppShell />,
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
