import { Link } from "react-router-dom";

import type { DashboardItem, DashboardPaceSummary, JsonValue } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { EmptyState } from "../../components/feedback/EmptyState.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { SetupGuide } from "../../components/onboarding/SetupGuide.tsx";
import { Panel } from "../../components/ui/Panel.tsx";
import { ProgressBar } from "../../components/ui/ProgressBar.tsx";
import { useDashboard } from "../../features/dashboard/useDashboard.ts";
import { formatCents, formatDate, formatDateTime, formatPercent } from "../../utils/format.ts";
import { formatInputCategoryList } from "../../utils/labels.ts";

const missingInputLabels: Record<string, { action: string; label: string; to: string }> = {
  active_goal: {
    action: "Create the active savings goal for this MVP.",
    label: "Active goal",
    to: routes.goal,
  },
  calculation_snapshot: {
    action: "Save valid goal and financial assumptions so the backend can calculate your pace.",
    label: "Calculation record",
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
        <Alert title="Dashboard unavailable" variant="error">
          <p>{dashboard.error}</p>
        </Alert>
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
    <PageHeader
      description="Backend-owned pace result for your active savings goal."
      title="Dashboard"
      titleId="dashboard-title"
    />
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
      <SetupGuide activeStep="dashboard" completedSteps={["goal", "profile", "income", "expenses"]} compact />

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
        <Panel className="goal-panel" title={item.goal.name}>
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
        </Panel>

        <Panel title="Current week">
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
        </Panel>

        <Panel title="Risk view">
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
        </Panel>
      </section>

      <section className="dashboard-grid secondary" aria-label="Calculation explanation">
        <Panel title="Latest calculation">
          <dl className="snapshot-list">
            <div>
              <dt>Calculated</dt>
              <dd>{formatDateTime(item.calculated_at)}</dd>
            </div>
            <div>
              <dt>Formula version</dt>
              <dd>{item.formula_version}</dd>
            </div>
          </dl>
          <Link className="text-link" to={routes.calculation}>
            View calculation record
          </Link>
        </Panel>

        <Panel title="Included assumptions">
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
        </Panel>

        <Panel title="Changed from previous">
          <p className="panel-copy">
            {changedInputCategories.length === 0
              ? "No previous calculation changes are available yet."
              : formatInputCategoryList(changedInputCategories)}
          </p>
          <p className="panel-copy">
            Weekly safe-to-spend delta: {weeklyDelta === null ? "Not available" : formatCents(weeklyDelta)}
          </p>
        </Panel>
      </section>
    </section>
  );
}

function SetupRequiredDashboard({ item }: { item: DashboardItem }) {
  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <DashboardHeader />
      <SetupGuide
        activeStep={item.goal === null ? "goal" : "profile"}
        completedSteps={item.goal === null ? [] : ["goal"]}
      />
      <EmptyState
        title="Finish setup to calculate your pace"
        description="The backend has not returned a complete dashboard result yet. Complete the missing MVP inputs below."
      />
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
