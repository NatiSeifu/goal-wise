import { routes } from "../../app/routes.ts";
import { PageShell } from "../../components/layout/PageShell.tsx";
import { ButtonLink } from "../../components/ui/Button.tsx";

export function LandingRoute() {
  return (
    <PageShell>
      <section className="intro-panel" aria-labelledby="intro-title">
        <h1 id="intro-title">GoalWise</h1>
        <p className="intro-copy">
          Plan one savings goal from manual assumptions, then let the backend calculate
          your weekly safe-to-spend amount and preserve each result as an immutable snapshot.
        </p>
        <div className="action-row" aria-label="GoalWise actions">
          <ButtonLink variant="primary" to={routes.register}>
            Create account
          </ButtonLink>
          <ButtonLink to={routes.dashboard}>
            Open dashboard
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
          <h2>Backend-owned money logic</h2>
          <p>
            React may format values returned by the API, but the official safe-to-spend,
            shortfall, pace status, and snapshot values stay owned by the backend.
          </p>
        </article>
        <article className="detail-panel" id="security">
          <h2>Session and CSRF boundary</h2>
          <p>
            Authenticated requests will include HTTP-only session cookies, and unsafe methods
            will send the CSRF header provided by the backend.
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
