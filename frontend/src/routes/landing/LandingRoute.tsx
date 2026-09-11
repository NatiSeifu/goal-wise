import { Navigate } from "react-router-dom";

import { routes } from "../../app/routes.ts";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageShell } from "../../components/layout/PageShell.tsx";
import { ButtonLink } from "../../components/ui/Button.tsx";
import { useAuth } from "../../features/auth/AuthProvider.tsx";

export function LandingRoute() {
  const auth = useAuth();

  if (auth.status === "checking") {
    return <RouteLoading label="Checking session" />;
  }

  if (auth.status === "authenticated") {
    return <Navigate replace to={routes.dashboard} />;
  }

  return (
    <PageShell>
      <section className="intro-panel" aria-labelledby="intro-title">
        <h1 id="intro-title">Know what you can spend each week.</h1>
        <p className="intro-copy">
          Set a savings goal. Add your cash, income, and expenses.
        </p>
        <div className="action-row" aria-label="GoalWise actions">
          <ButtonLink variant="primary" to={routes.register}>
            Create account
          </ButtonLink>
          <ButtonLink to={routes.login}>
            Sign in
          </ButtonLink>
        </div>
      </section>
    </PageShell>
  );
}
