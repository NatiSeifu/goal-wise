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
import { formatCents, formatDate } from "../../utils/format.ts";
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
      <div className="dashboard-layout">
        <div className="dashboard-main-column">
          <section className="metric-hero" aria-labelledby="safe-to-spend-title">
            <div className="metric-hero-copy">
              <h2 id="safe-to-spend-title">Weekly safe-to-spend</h2>
              <p className="metric-value">{formatCents(pace.weekly_safe_to_spend_cents)}</p>
              <p className="metric-hero-note">
                {pace.pace_status === "At Risk" ? "Your forecast still covers the goal." : "Your plan is tracking toward the goal."}
              </p>
              <Link className="button metric-hero-action" to={routes.financialInputs}>Adjust plan <span aria-hidden="true">→</span></Link>
            </div>
            <div className="metric-hero-visual" aria-hidden="true">
              <img className={`metric-hero-logo ${logoTone(pace.pace_status)}`} src={`/goalwise-${logoTone(pace.pace_status)}.png`} alt="" />
            </div>
            <div className="metric-hero-aside">
              <strong>{formatCents(item.goal.current_saved_cents)}</strong>
              <span>saved of {formatCents(item.goal.target_cents)}</span>
              <span className="metric-hero-divider" />
              <strong>{Math.round(pace.progress_percentage)}%</strong>
              <span>complete</span>
            </div>
          </section>

          <section className="dashboard-goal-card" aria-labelledby="goal-story-title">
            <div className="goal-card-heading">
              <div>
                <h2 id="goal-story-title">{item.goal.name}</h2>
                <p>One goal, clearly in view.</p>
              </div>
              <Link className="icon-link" aria-label="Edit goal" to={routes.goal}>→</Link>
            </div>
            <ProgressBar label="Goal progress" value={pace.progress_percentage} />
            <div className="goal-summary">
              <span><strong>{formatCents(item.goal.current_saved_cents)}</strong> of {formatCents(item.goal.target_cents)}</span>
              <span>{formatDate(item.goal.target_date)} · {pace.remaining_weeks} weeks left</span>
            </div>
            {pace.projected_shortfall_cents > 0 ? (
              <p className="plan-warning">
                Projected shortfall: <strong>{formatCents(pace.projected_shortfall_cents)}</strong>.{' '}
                <Link to={routes.financialInputs}>Review inputs</Link>
              </p>
            ) : pace.pace_status === "At Risk" ? (
              <p className="plan-warning">
                Savings are behind pace; your forecast still covers the goal.{' '}
                <Link to={routes.goal}>Review goal</Link>
              </p>
            ) : null}
          </section>

          <section className="dashboard-panel dashboard-inputs-card" aria-labelledby="inputs-card-title">
            <div className="section-heading-row">
              <div>
                <h2 id="inputs-card-title">Income & expenses</h2>
                <p className="panel-subtitle">The inputs behind this plan.</p>
              </div>
              <Link className="text-link" to={routes.financialInputs}>Edit inputs</Link>
            </div>
            {unconfirmedIncome > 0 ? (
              <p className="plan-warning">
                {unconfirmedIncome} unconfirmed income {unconfirmedIncome === 1 ? "source is" : "sources are"} excluded.{' '}
                <Link to={`${routes.financialInputs}#income-sources`}>Review income</Link>
              </p>
            ) : null}
            <UpcomingPlan snapshot={snapshot} compact />
          </section>
        </div>

        <aside className="dashboard-rail">
          <section className="forecast-card" aria-labelledby="forecast-title">
            <svg className="forecast-timeseries" viewBox="0 0 260 110" preserveAspectRatio="none" aria-hidden="true">
              <path d="M0 87 C22 82 30 70 52 74 S79 88 101 69 S126 62 145 67 S169 73 185 50 S210 45 226 48 S246 36 260 18" />
            </svg>
            <div className="forecast-heading">
              <span className={`status-pill status-pill-${statusTone(pace.pace_status)}`}>
                {paceStatusLabel(pace.pace_status)}
              </span>
              <Link className="icon-link" aria-label="View plan details" to={routes.calculation}>→</Link>
            </div>
            <h2 id="forecast-title">Target date</h2>
            <strong>{formatDate(item.goal.target_date)}</strong>
            <p>{pace.remaining_weeks} weeks left</p>
            <div className="forecast-note">{pace.projected_shortfall_cents > 0 ? "Review your inputs to understand the gap." : "Your saved inputs still cover the forecast."}</div>
          </section>
          <AIExplanationPanel key={item.snapshot_id} pace={pace} snapshotId={item.snapshot_id ?? ""} />
          <section className="dashboard-panel upcoming-rail-card" aria-labelledby="upcoming-rail-title">
            <div className="section-heading-row">
              <h2 id="upcoming-rail-title">Upcoming</h2>
              <Link className="text-link" to={routes.financialInputs}>View all</Link>
            </div>
            <UpcomingPlan snapshot={snapshot} compact />
          </section>
        </aside>
      </div>
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

function UpcomingPlan({ snapshot, compact = false }: { snapshot: CalculationSnapshotResponse | null; compact?: boolean }) {
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
    <section className={`upcoming-plan${compact ? " upcoming-plan-compact" : ""}`} aria-label={compact ? "Upcoming plan items" : "Income and expenses"}>
      {compact ? null : (
        <div className="section-heading-row section-heading-row-tight">
          <div>
            <h2 id="upcoming-plan-title">Income & expenses</h2>
          </div>
          <Link className="text-link" to={routes.financialInputs}>Edit inputs</Link>
        </div>
      )}
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

function logoTone(status: string) {
  if (status === "Completed") return "logo-completed";
  if (status === "Ahead") return "logo-ahead";
  if (status === "At Risk") return "logo-at-risk";
  if (status === "Off Pace") return "logo-off-pace";
  return "logo-on-track";
}
