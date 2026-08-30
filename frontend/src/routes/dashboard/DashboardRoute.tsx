import { Link } from "react-router-dom";

import type { DashboardItem, DashboardPaceSummary, JsonValue } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { AIExplanationPanel } from "../../components/dashboard/AIExplanationPanel.tsx";
import { EmptyState } from "../../components/feedback/EmptyState.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { SetupGuide } from "../../components/onboarding/SetupGuide.tsx";
import { Panel } from "../../components/ui/Panel.tsx";
import { ProgressBar } from "../../components/ui/ProgressBar.tsx";
import { useDashboard } from "../../features/dashboard/useDashboard.ts";
import { setupGuideStateFromDashboard } from "../../features/setup/setupGuideState.ts";
import { formatCents, formatDate, formatDateTime } from "../../utils/format.ts";
import { formatInputCategoryList, paceStatusDescription, paceStatusLabel } from "../../utils/labels.ts";

const missingInputLabels: Record<string, { action: string; label: string; to: string }> = {
  active_goal: {
    action: "Create the active savings goal for this MVP.",
    label: "Active goal",
    to: routes.goal,
  },
  calculation_snapshot: {
    action: "Save your goal and planning assumptions so GoalWise can calculate your weekly plan.",
    label: "Plan calculation",
    to: routes.financialInputs,
  },
  financial_profile: {
    action: "Add starting cash, balance date, and reserve buffer.",
    label: "Cash picture",
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
      description="Your current savings progress and weekly spending guidance."
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
  const weeklyChangeLabel = formatWeeklyChange(weeklyDelta);
  const hasPlanChanges = changedInputCategories.length > 0 || weeklyDelta !== null;

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <DashboardHeader />

      <section className="metric-hero" aria-labelledby="safe-to-spend-title">
        <div>
          <h2 id="safe-to-spend-title">Weekly safe-to-spend</h2>
          <p className="metric-value">{formatCents(pace.weekly_safe_to_spend_cents)}</p>
          <p className="metric-support">
            This is the amount left for weekly spending while staying aligned with your goal.
          </p>
          <PaceStatusExplanation goal={item.goal} pace={pace} />
        </div>
        <div className="status-stack">
          <span className="status-pill">{paceStatusLabel(pace.pace_status)}</span>
          <span className="status-context">{paceStatusDescription(pace.pace_status)}</span>
          <span>Updated {formatDateTime(item.calculated_at)}</span>
        </div>
      </section>

      <div className="dashboard-primary-layout">
        <div className="dashboard-main-column">
          <section className="dashboard-overview" aria-label="Plan summary">
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

            <div className="dashboard-supporting-cards">
              <Panel title="Current week">
                <dl className="dashboard-feature-metric">
                  <div>
                    <dt>Weekly allowance</dt>
                    <dd>{formatCents(pace.weekly_safe_to_spend_cents)}</dd>
                  </div>
                </dl>
                <dl className="dashboard-supporting-detail">
                  <div>
                    <dt>Weeks to target</dt>
                    <dd>{pace.remaining_weeks}</dd>
                  </div>
                </dl>
              </Panel>

              <Panel title="Goal outlook">
                <dl className="dashboard-feature-metric">
                  <div>
                    <dt>Projected shortfall</dt>
                    <dd>{formatCents(pace.projected_shortfall_cents)}</dd>
                  </div>
                </dl>
                <p className="dashboard-feature-support">
                  {pace.projected_shortfall_cents === 0
                    ? "Your current forecast covers the remaining goal amount."
                    : "Your current forecast does not cover the remaining goal amount yet."}
                </p>
              </Panel>
            </div>
          </section>

          <section className={`dashboard-context${hasPlanChanges ? "" : " single"}`} aria-label="Plan context">
            <div className="dashboard-context-block">
              <h2>Plan context</h2>
              <p className="panel-copy">Your dashboard is based on these saved assumptions.</p>
              <dl className="dashboard-context-summary">
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
              <Link className="text-link" to={routes.calculation}>
                View plan details
              </Link>
            </div>

            {hasPlanChanges ? (
              <div className="dashboard-context-block">
                <h2>What changed</h2>
                <p className="panel-copy">{formatInputCategoryList(changedInputCategories)}</p>
                <p className="panel-copy">{weeklyChangeLabel}</p>
              </div>
            ) : null}
          </section>
        </div>

        <AIExplanationPanel key={item.snapshot_id} pace={pace} snapshotId={item.snapshot_id ?? ""} />
      </div>
    </section>
  );
}

function PaceStatusExplanation({ goal, pace }: { goal: NonNullable<DashboardItem["goal"]>; pace: DashboardPaceSummary }) {
  const progressDelta = pace.expected_savings_to_date_cents - goal.current_saved_cents;
  if (
    pace.pace_status !== "At Risk" ||
    !Number.isFinite(pace.expected_savings_to_date_cents) ||
    progressDelta <= 0
  ) {
    return null;
  }

  return (
    <p className="metric-status-explanation">
      Your saved progress is {formatCents(progressDelta)} behind the target pace. The {formatCents(pace.weekly_safe_to_spend_cents)} shown above is still available based on your forecasted cash flow.
    </p>
  );
}

function SetupRequiredDashboard({ item }: { item: DashboardItem }) {
  const guideState = setupGuideStateFromDashboard(item);

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <DashboardHeader />
      <SetupGuide activeStep={guideState.activeStep} completedSteps={guideState.completedSteps} />
      <EmptyState
        title="Finish setup to calculate your weekly plan"
        description="GoalWise needs a complete goal, cash picture, and confirmed reserve before it can show your weekly number."
      />
      <div className="setup-list" aria-label="Missing inputs">
        {item.missing_inputs.map((missingInput) => {
          const detail = missingInputLabels[missingInput] ?? {
            action: "Complete this setup item.",
            label: "Setup item",
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

function formatWeeklyChange(deltaCents: number | null) {
  if (deltaCents === null) {
    return "Weekly safe-to-spend change is not available yet.";
  }
  if (deltaCents === 0) {
    return "Weekly safe-to-spend stayed the same.";
  }
  const direction = deltaCents > 0 ? "increased" : "decreased";
  return `Weekly safe-to-spend ${direction} by ${formatCents(Math.abs(deltaCents))}.`;
}
