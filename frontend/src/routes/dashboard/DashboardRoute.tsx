import { Link } from "react-router-dom";

import type { CalculationSnapshotResponse, DashboardItem, DashboardPaceSummary, JsonValue } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { AIExplanationPanel } from "../../components/dashboard/AIExplanationPanel.tsx";
import { EmptyState } from "../../components/feedback/EmptyState.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { ButtonLink } from "../../components/ui/Button.tsx";
import { ProgressBar } from "../../components/ui/ProgressBar.tsx";
import { useDashboard } from "../../features/dashboard/useDashboard.ts";
import { useLatestCalculationSnapshot } from "../../features/snapshots/useLatestCalculationSnapshot.ts";
import { formatCents, formatDate, formatDateTime } from "../../utils/format.ts";
import {
  classificationLabel,
  formatInputCategoryList,
  frequencyLabel,
  paceStatusLabel,
} from "../../utils/labels.ts";

export function DashboardRoute() {
  const dashboard = useDashboard();
  const snapshot = useLatestCalculationSnapshot();

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

  return (
    <ReadyDashboard
      item={dashboard.data}
      pace={dashboard.data.pace}
      snapshot={snapshot.status === "ready" ? snapshot.data : null}
    />
  );
}

function DashboardHeader() {
  return (
    <header className="dashboard-page-header">
      <div>
        <h1 id="dashboard-title">Dashboard</h1>
      </div>
      <Link className="dashboard-header-link" to={routes.financialInputs}>
        Adjust plan
      </Link>
    </header>
  );
}

function ReadyDashboard({
  item,
  pace,
  snapshot,
}: {
  item: DashboardItem;
  pace: DashboardPaceSummary;
  snapshot: CalculationSnapshotResponse | null;
}) {
  if (item.goal === null) {
    return null;
  }

  const explanationSummary = getJsonObject(item.explanation, "summary");
  const changedInputCategories = getStringList(item.changed_from_previous, "changed_input_categories");
  const weeklyDelta = getNumberValue(item.changed_from_previous, "weekly_safe_to_spend_delta_cents");
  const weeklyChangeLabel = formatWeeklyChange(weeklyDelta);
  const unconfirmedIncome = getNumberValue(explanationSummary, "unconfirmed_income_count") ?? 0;

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <DashboardHeader />
      <section className="metric-hero" aria-labelledby="safe-to-spend-title">
        <div>
          <h2 id="safe-to-spend-title">Weekly safe-to-spend</h2>
          <p className="metric-value">{formatCents(pace.weekly_safe_to_spend_cents)}</p>
        </div>
        <div className="metric-hero-aside">
          <Link className="text-link" to={routes.calculation}>View plan details</Link>
          <span className="status-updated">Updated {formatDateTime(item.calculated_at)}</span>
        </div>
      </section>

      <AIExplanationPanel key={item.snapshot_id} pace={pace} snapshotId={item.snapshot_id ?? ""} />

      <section className="dashboard-goal-story" aria-labelledby="goal-story-title">
        <div className="section-heading-row">
          <h2 id="goal-story-title">{item.goal.name}</h2>
          <span className={`status-pill status-pill-${statusTone(pace.pace_status)}`}>
            {paceStatusLabel(pace.pace_status)}
          </span>
        </div>
        <ProgressBar label="Goal progress" value={pace.progress_percentage} />
        <div className="goal-summary">
          <span><strong>{formatCents(item.goal.current_saved_cents)}</strong> of {formatCents(item.goal.target_cents)} saved</span>
          <span>{formatDate(item.goal.target_date)} · {pace.remaining_weeks} weeks left</span>
        </div>
        {pace.projected_shortfall_cents > 0 ? (
          <p className="plan-warning">
            Projected shortfall: <strong>{formatCents(pace.projected_shortfall_cents)}</strong>.{' '}
            <Link to={routes.financialInputs}>Review income and expenses</Link>
          </p>
        ) : pace.pace_status === "At Risk" ? (
          <p className="plan-warning">
            Savings are behind pace; your forecast still covers the goal.{' '}
            <Link to={routes.goal}>Update savings</Link>
          </p>
        ) : null}
        <Link className="text-link" to={routes.goal}>Edit goal</Link>
      </section>

      {unconfirmedIncome > 0 ? (
        <p className="plan-warning">
          {unconfirmedIncome} unconfirmed income {unconfirmedIncome === 1 ? "source is" : "sources are"} excluded.{' '}
          <Link to={`${routes.financialInputs}#income-sources`}>Review income</Link>
        </p>
      ) : null}
      <UpcomingPlan snapshot={snapshot} />
      {changedInputCategories.length > 0 || (weeklyDelta !== null && weeklyDelta !== 0) ? (
        <details className="plan-changes">
          <summary>Latest changes</summary>
          {changedInputCategories.length > 0 ? <p>{formatInputCategoryList(changedInputCategories)}</p> : null}
          {weeklyDelta === null ? null : <p>{weeklyChangeLabel}</p>}
        </details>
      ) : null}
    </section>
  );
}

function UpcomingPlan({ snapshot }: { snapshot: CalculationSnapshotResponse | null }) {
  if (snapshot === null) {
    return null;
  }

  const input = snapshot.normalized_input_json;
  const income = getObjectArray(input, "income_sources").map((item) => ({ ...item, kind: "income" as const }));
  const expenses = getObjectArray(input, "planned_expenses").map((item) => ({ ...item, kind: "expense" as const }));
  const items = [...income, ...expenses]
    .filter((item) => getStringValue(item, "next_date") !== null)
    .sort((left, right) => (getStringValue(left, "next_date") ?? "").localeCompare(getStringValue(right, "next_date") ?? ""))
    .slice(0, 4);

  if (items.length === 0) return null;

  return (
    <section className="upcoming-plan" aria-labelledby="upcoming-plan-title">
      <div className="section-heading-row section-heading-row-tight">
        <div>
          <h2 id="upcoming-plan-title">Income & expenses</h2>
        </div>
        <Link className="text-link" to={routes.financialInputs}>Edit inputs</Link>
      </div>
        <ul className="upcoming-list">
          {items.map((item) => {
            const kind = item.kind;
            const name = getStringValue(item, "name") ?? "Unnamed item";
            const amount = getNumberValue(item, "amount_cents");
            const nextDate = getStringValue(item, "next_date");
            const frequency = getStringValue(item, "frequency");
            const detail = kind === "income"
              ? getStringValue(item, "confidence") === "confirmed" ? "Confirmed income" : "Needs confirmation"
              : classificationLabel(getStringValue(item, "classification"));

            return (
              <li key={`${kind}-${getStringValue(item, "id") ?? name}`}>
                <span className={`upcoming-kind upcoming-kind-${kind}`} aria-hidden="true" />
                <span className="upcoming-name">
                  <strong>{name}</strong>
                  <small>{nextDate === null ? "Date unavailable" : formatDate(nextDate)} · {detail}</small>
                </span>
                <span className="upcoming-amount">
                  <strong>{amount === null ? "Not available" : formatCents(amount)}</strong>
                  <small>{frequency === null ? "" : frequencyLabel(frequency)}</small>
                </span>
              </li>
            );
          })}
        </ul>
    </section>
  );
}

function SetupRequiredDashboard({ item }: { item: DashboardItem }) {
  const needsGoal = item.missing_inputs.includes("active_goal");
  const needsReserve = item.missing_inputs.includes("reserve_buffer_confirmation");
  const needsCash = item.missing_inputs.includes("financial_profile");
  const action = needsGoal ? "Create goal" : needsCash ? "Add cash balance" : needsReserve ? "Confirm reserve" : "Review inputs";
  const title = needsGoal ? "No savings goal yet" : needsCash ? "Add your cash balance" : needsReserve ? "Confirm your reserve" : "No calculation yet";

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <DashboardHeader />
      <EmptyState
        title={title}
        action={<ButtonLink variant="primary" to={needsGoal ? routes.goal : `${routes.financialInputs}#cash-picture`}>{action}</ButtonLink>}
      />
    </section>
  );
}

function getJsonObject(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : null;
}

function getObjectArray(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return value
    ? Array.isArray(value)
      ? value.filter(
          (item): item is Record<string, JsonValue> =>
            item !== null && typeof item === "object" && !Array.isArray(item),
        )
      : []
    : [];
}

function getStringValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return typeof value === "string" ? value : null;
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

function statusTone(status: string) {
  const normalized = status.toLowerCase();
  if (normalized.includes("risk") || normalized.includes("pace")) {
    return "warning";
  }
  if (normalized === "completed" || normalized === "ahead" || normalized.includes("track")) {
    return "positive";
  }
  return "neutral";
}
