import { Link } from "react-router-dom";

import type { DashboardItem, DashboardPaceSummary, JsonValue } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { ProgressBar } from "../../components/ui/ProgressBar.tsx";
import { useDashboard } from "../../features/dashboard/useDashboard.ts";
import { formatCents, formatDate, formatDateTime, formatPercent } from "../../utils/format.ts";

const missingInputLabels: Record<string, { action: string; label: string; to: string }> = {
  active_goal: {
    action: "Create the active savings goal for this MVP.",
    label: "Active goal",
    to: routes.goal,
  },
  calculation_snapshot: {
    action: "Save valid goal and financial assumptions so the backend can create a snapshot.",
    label: "Calculation snapshot",
    to: routes.financialInputs,
  },
  financial_profile: {
    action: "Add starting cash, balance date, and reserve buffer.",
    label: "Financial profile",
    to: routes.financialInputs,
  },
  reserve_buffer_confirmation: {
    action: "Confirm the reserve buffer before calculating safe-to-spend.",
    label: "Reserve buffer confirmation",
    to: routes.financialInputs,
  },
};

export function DashboardRoute() {
  const dashboard = useDashboard();

  if (dashboard.status === "loading") {
    return <RouteLoading fullPage={false} label="Loading dashboard" />;
  }

  if (dashboard.status === "error") {
    return (
      <section className="dashboard-page" aria-labelledby="dashboard-title">
        <DashboardHeader />
        <div className="state-panel error">
          <h2>Dashboard unavailable</h2>
          <p>{dashboard.error}</p>
        </div>
      </section>
    );
  }

  if (dashboard.data.status !== "ready" || dashboard.data.goal === null || dashboard.data.pace === null) {
    return <SetupRequiredDashboard item={dashboard.data} />;
  }

  return <ReadyDashboard item={dashboard.data} pace={dashboard.data.pace} />;
}

function DashboardHeader() {
  return (
    <header className="dashboard-header">
      <div>
        <h1 id="dashboard-title">Dashboard</h1>
        <p>Backend-owned pace result for your active savings goal.</p>
      </div>
    </header>
  );
}

function ReadyDashboard({ item, pace }: { item: DashboardItem; pace: DashboardPaceSummary }) {
  if (item.goal === null) {
    return null;
  }

  const explanationSummary = getJsonObject(item.explanation, "summary");
  const changedInputCategories = getStringList(item.changed_from_previous, "changed_input_categories");
  const weeklyDelta = getNumberValue(item.changed_from_previous, "weekly_safe_to_spend_delta_cents");

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <DashboardHeader />

      <section className="metric-hero" aria-labelledby="safe-to-spend-title">
        <div>
          <h2 id="safe-to-spend-title">Weekly safe-to-spend</h2>
          <p className="metric-value">{formatCents(pace.weekly_safe_to_spend_cents)}</p>
        </div>
        <div className="status-stack">
          <span className="status-pill">{pace.pace_status}</span>
          <span>Formula {item.formula_version}</span>
        </div>
      </section>

      <section className="dashboard-grid" aria-label="Plan summary">
        <article className="dashboard-panel goal-panel">
          <h2>{item.goal.name}</h2>
          <ProgressBar label="Goal progress" value={pace.progress_percentage} />
          <dl className="metric-list">
            <div>
              <dt>Saved</dt>
              <dd>{formatCents(item.goal.current_saved_cents)}</dd>
            </div>
            <div>
              <dt>Target</dt>
              <dd>{formatCents(item.goal.target_cents)}</dd>
            </div>
            <div>
              <dt>Target date</dt>
              <dd>{formatDate(item.goal.target_date)}</dd>
            </div>
          </dl>
        </article>

        <article className="dashboard-panel">
          <h2>Current week</h2>
          <dl className="metric-list compact">
            <div>
              <dt>Opening allowance</dt>
              <dd>{formatCents(pace.current_week_opening_allowance_cents)}</dd>
            </div>
            <div>
              <dt>Remainder</dt>
              <dd>{formatCents(pace.current_week_remainder_cents)}</dd>
            </div>
            <div>
              <dt>Remaining weeks</dt>
              <dd>{pace.remaining_weeks}</dd>
            </div>
          </dl>
        </article>

        <article className="dashboard-panel">
          <h2>Risk view</h2>
          <dl className="metric-list compact">
            <div>
              <dt>Projected shortfall</dt>
              <dd>{formatCents(pace.projected_shortfall_cents)}</dd>
            </div>
            <div>
              <dt>Progress</dt>
              <dd>{formatPercent(pace.progress_percentage)}</dd>
            </div>
            <div>
              <dt>Calculated</dt>
              <dd>{formatDateTime(item.calculated_at)}</dd>
            </div>
          </dl>
        </article>
      </section>

      <section className="dashboard-grid secondary" aria-label="Snapshot explanation">
        <article className="dashboard-panel">
          <h2>Snapshot trail</h2>
          <dl className="snapshot-list">
            <div>
              <dt>Snapshot ID</dt>
              <dd>{item.snapshot_id}</dd>
            </div>
            <div>
              <dt>Formula version</dt>
              <dd>{item.formula_version}</dd>
            </div>
          </dl>
          <Link className="text-link" to={routes.calculation}>
            View calculation details
          </Link>
        </article>

        <article className="dashboard-panel">
          <h2>Included assumptions</h2>
          <dl className="metric-list compact">
            <div>
              <dt>Confirmed income sources</dt>
              <dd>{getNumberValue(explanationSummary, "confirmed_income_count") ?? "0"}</dd>
            </div>
            <div>
              <dt>Planned expenses</dt>
              <dd>{getNumberValue(explanationSummary, "planned_expense_count") ?? "0"}</dd>
            </div>
            <div>
              <dt>Unconfirmed income</dt>
              <dd>{getNumberValue(explanationSummary, "unconfirmed_income_count") ?? "0"}</dd>
            </div>
          </dl>
        </article>

        <article className="dashboard-panel">
          <h2>Changed from previous</h2>
          <p className="panel-copy">
            {changedInputCategories.length === 0
              ? "No previous snapshot changes are reported by the backend."
              : changedInputCategories.join(", ")}
          </p>
          <p className="panel-copy">
            Weekly safe-to-spend delta: {weeklyDelta === null ? "Not available" : formatCents(weeklyDelta)}
          </p>
        </article>
      </section>
    </section>
  );
}

function SetupRequiredDashboard({ item }: { item: DashboardItem }) {
  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <DashboardHeader />
      <div className="state-panel">
        <h2>Finish setup to calculate your pace</h2>
        <p>
          The backend has not returned a complete dashboard result yet. Complete the missing MVP inputs below.
        </p>
      </div>
      <div className="setup-list" aria-label="Missing inputs">
        {item.missing_inputs.map((missingInput) => {
          const detail = missingInputLabels[missingInput] ?? {
            action: "Complete this backend-required setup item.",
            label: missingInput,
            to: routes.financialInputs,
          };
          return (
            <Link className="setup-item" key={missingInput} to={detail.to}>
              <span>{detail.label}</span>
              <span>{detail.action}</span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}

function getJsonObject(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : null;
}

function getNumberValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return typeof value === "number" ? value : null;
}

function getStringList(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}
