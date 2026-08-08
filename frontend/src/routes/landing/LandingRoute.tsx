import { PageShell } from "../../components/layout/PageShell.tsx";

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
          <a className="button primary" href="#mvp-boundary">
            MVP boundary
          </a>
          <a className="button secondary" href="#scaffold-details">
            Scaffold details
          </a>
        </div>
      </section>
      <section className="detail-grid" aria-label="Frontend scaffold details">
        <article className="detail-panel" id="mvp-boundary">
          <h2>Backend-owned money logic</h2>
          <p>
            React may format values returned by the API, but the official safe-to-spend,
            shortfall, pace status, and snapshot values stay owned by the backend.
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
