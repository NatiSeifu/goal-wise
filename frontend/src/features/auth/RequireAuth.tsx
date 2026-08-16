import { Navigate, useLocation, type Location } from "react-router-dom";
import type { ReactNode } from "react";

import { routes } from "../../app/routes.ts";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { useAuth } from "./AuthProvider.tsx";

export type AuthRedirectState = {
  from?: Location;
};

type RequireAuthProps = {
  children: ReactNode;
};

export function RequireAuth({ children }: RequireAuthProps) {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "checking") {
    return <RouteLoading label="Checking your session" />;
  }

  if (status === "unauthenticated") {
    return <Navigate replace state={{ from: location } satisfies AuthRedirectState} to={routes.login} />;
  }

  return children;
}
