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
        <h1 id="intro-title">GoalWise</h1>
        <p className="intro-copy">
          Plan one savings goal from manual assumptions, then see a weekly safe-to-spend
          amount you can review and revisit.
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
      <nav className="landing-links" aria-label="Landing page details">
        <a href="#mvp-boundary">MVP boundary</a>
        <a href="#security">Security</a>
        <a href="#structure">Structure</a>
      </nav>
      <section className="detail-grid" aria-label="GoalWise product details">
        <article className="detail-panel" id="mvp-boundary">
          <h2>Consistent money logic</h2>
          <p>
            GoalWise uses deterministic rules for safe-to-spend, shortfall, plan status,
            and saved plan details.
          </p>
        </article>
        <article className="detail-panel" id="security">
          <h2>Private account access</h2>
          <p>
            Your plan requires sign-in, protected sessions, and request checks before
            account changes are accepted.
          </p>
        </article>
        <article className="detail-panel" id="structure">
          <h2>Focused MVP workflow</h2>
          <p>
            The current app supports account access, one active goal, manual inputs,
            deterministic dashboard results, and calculation details.
          </p>
        </article>
      </section>
    </PageShell>
  );
}
