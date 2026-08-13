import { routes } from "../../app/routes.ts";
import { PageShell } from "../../components/layout/PageShell.tsx";
import { ButtonLink } from "../../components/ui/Button.tsx";

export function LandingRoute() {
  return (
    <PageShell>
      <section className="intro-panel" aria-labelledby="intro-title">
        <h1 id="intro-title">GoalWise frontend foundation</h1>
        <p className="intro-copy">
          This scaffold proves the Vite frontend builds cleanly while the product UI remains
          grounded in the MVP: one active goal, manual financial assumptions, deterministic
          backend calculations, and immutable snapshots.
        </p>
        <div className="action-row" aria-label="Frontend status">
          <ButtonLink variant="primary" to={routes.register}>
            Create account
          </ButtonLink>
          <ButtonLink to={routes.dashboard}>
            View app shell
          </ButtonLink>
        </div>
      </section>
      <nav className="landing-links" aria-label="Landing page details">
        <a href="#mvp-boundary">MVP boundary</a>
        <a href="#security">Security</a>
        <a href="#scaffold-details">Scaffold details</a>
      </nav>
      <section className="detail-grid" aria-label="Frontend scaffold details">
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
        <article className="detail-panel" id="scaffold-details">
          <h2>Composable app structure</h2>
          <p>
            App setup, route screens, layout components, and style tokens are split so the
            visual system can evolve without collapsing into a single mockup file.
          </p>
        </article>
      </section>
    </PageShell>
  );
}
