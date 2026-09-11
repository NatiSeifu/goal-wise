import type { JsonValue } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { EmptyState } from "../../components/feedback/EmptyState.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { ButtonLink } from "../../components/ui/Button.tsx";
import { useLatestCalculationSnapshot } from "../../features/snapshots/useLatestCalculationSnapshot.ts";
import { formatCents, formatDate, formatDateTime, formatPercent } from "../../utils/format.ts";
import {
  classificationLabel,
  frequencyLabel,
  paceStatusLabel,
} from "../../utils/labels.ts";

export function CalculationRoute() {
  const snapshot = useLatestCalculationSnapshot();

  if (snapshot.status === "loading") {
    return <RouteLoading fullPage={false} label="Loading plan details" />;
  }

  if (snapshot.status === "error") {
    return (
      <section className="dashboard-page" aria-labelledby="calculation-title">
        <CalculationHeader />
        <Alert title="Calculation unavailable" variant="error">
          <p>{snapshot.error}</p>
        </Alert>
      </section>
    );
  }

  if (snapshot.data === null) {
    return (
      <section className="dashboard-page" aria-labelledby="calculation-title">
        <CalculationHeader />
        <EmptyState
          title="No calculation yet"
          description="Save a valid goal and financial assumptions before viewing plan details."
          action={
            <ButtonLink variant="primary" to={routes.financialInputs}>
              Open financial inputs
            </ButtonLink>
          }
        />
      </section>
    );
  }

  const input = snapshot.data.normalized_input_json;
  const goal = getJsonObject(input, "goal");
  const profile = getJsonObject(input, "financial_profile");
  const outputs = getJsonObject(snapshot.data.result_json, "outputs");
  const explanation = getJsonObject(snapshot.data.result_json, "explanation");
  const summary = getJsonObject(explanation, "summary");
  const incomeSources = getObjectArray(input, "income_sources");
  const plannedExpenses = getObjectArray(input, "planned_expenses");
  const includedIncomeIds = getStringArray(explanation, "included_income_source_ids");
  const includedExpenseIds = getStringArray(explanation, "included_planned_expense_ids");
  const paceStatus = getStringValue(outputs, "pace_status");
  const safeToSpend = getNumberValue(outputs, "weekly_safe_to_spend_cents");
  const goalName = getStringValue(goal, "name") ?? "your goal";

  return (
    <section className="calculation-page" aria-labelledby="calculation-title">
      <CalculationHeader />
      <p className="calculation-meta">Last calculated {formatDateTime(snapshot.data.calculated_at)}</p>

      <section className="calculation-hero" aria-labelledby="calculation-answer-title">
        <div>
          <h2 id="calculation-answer-title">
            {safeToSpend === null ? "Your weekly plan" : `You can spend ${formatCents(safeToSpend)} each week`}
          </h2>
        </div>
        <div className={`calculation-status calculation-status-${statusTone(paceStatus)}`}>
          <span className="status-dot" aria-hidden="true" />
          <div>
            <strong>{paceStatus === null ? "Status unavailable" : paceStatusLabel(paceStatus)}</strong>
          </div>
        </div>
      </section>

      <section className="calculation-board" aria-label="How the plan is calculated">
        <div className="calculation-left-column">
          <section className="calculation-panel calculation-breakdown" aria-labelledby="calculation-breakdown-title">
            <div className="section-heading-row section-heading-row-tight">
              <div>
                <h2 id="calculation-breakdown-title">Calculation</h2>
              </div>
            </div>
            <div className="calculation-ledger">
              <LedgerRow label="Cash available now" value={moneyValue(outputs, "current_cash_cents")} />
              <LedgerRow label="Confirmed income before the target" value={moneyValue(outputs, "confirmed_future_income_cents")} sign="plus" />
              <LedgerRow label="Planned expenses before the target" value={moneyValue(outputs, "planned_future_expenses_cents")} sign="minus" />
              <LedgerRow label="Protected reserve" value={moneyValue(outputs, "reserve_buffer_cents")} sign="minus" />
              <LedgerRow label="Forecast resources" value={moneyValue(outputs, "forecast_resources_cents")} emphasis />
              <LedgerRow label="Still needed for goal" value={moneyValue(outputs, "goal_gap_cents")} sign="minus" />
              <LedgerRow label="Available to spend" value={moneyValue(outputs, "discretionary_capacity_cents")} emphasis />
              <LedgerRow label="Weeks remaining" value={numberValue(outputs, "remaining_weeks")} />
              <LedgerRow label="Weekly safe-to-spend" value={moneyValue(outputs, "weekly_safe_to_spend_cents")} emphasis />
            </div>
            {(getNumberValue(summary, "unconfirmed_income_count") ?? 0) > 0 ? (
              <p className="calculation-note">Unconfirmed income is excluded.</p>
            ) : null}
          </section>

          <section className="calculation-panel calculation-inputs" aria-labelledby="calculation-inputs-title">
            <div className="section-heading-row section-heading-row-tight">
              <div>
                <h2 id="calculation-inputs-title">Inputs</h2>
              </div>
              <ButtonLink to={routes.financialInputs}>Edit inputs</ButtonLink>
            </div>
            <dl className="calculation-counts">
              <Fact label="Income sources" value={numberValue(summary, "confirmed_income_count", "confirmed")} />
              <Fact label="Planned expenses" value={numberValue(summary, "planned_expense_count")} />
              <Fact label="Needs confirmation" value={numberValue(summary, "unconfirmed_income_count")} />
              <Fact label="Balance date" value={dateValue(profile, "balance_as_of_date")} />
            </dl>
          </section>
        </div>

        <div className="calculation-right-column">
          <section className="calculation-panel calculation-outlook" aria-labelledby="calculation-outlook-title">
            <h2 id="calculation-outlook-title">Goal</h2>
            <dl className="calculation-facts">
              <Fact label="Goal" value={goalName} />
              <Fact label="Saved so far" value={moneyValue(goal, "current_saved_cents")} />
              <Fact label="Goal target" value={moneyValue(goal, "target_cents")} />
              <Fact label="Time remaining" value={numberValue(outputs, "remaining_weeks", "weeks")} />
              <Fact label="Progress" value={percentValue(outputs, "progress_percentage")} />
              <Fact label="Projected shortfall" value={moneyValue(outputs, "projected_shortfall_cents")} />
            </dl>
          </section>


        </div>
      </section>

      <section className="calculation-advanced" aria-labelledby="calculation-advanced-title">
        <div>
          <h2 id="calculation-advanced-title">Calculation details</h2>
        </div>
        <details>
          <summary>Income included ({includedIncomeIds.length})</summary>
          <SnapshotItemList
            emptyLabel="No confirmed income is included in this plan."
            items={incomeSources.filter((item) => includedIncomeIds.includes(getStringValue(item, "id") ?? ""))}
            kind="income"
          />
        </details>
        <details>
          <summary>Expenses included ({includedExpenseIds.length})</summary>
          <SnapshotItemList
            emptyLabel="No planned expenses are included in this plan."
            items={plannedExpenses.filter((item) => includedExpenseIds.includes(getStringValue(item, "id") ?? ""))}
            kind="expense"
          />
        </details>

      </section>
    </section>
  );
}

function CalculationHeader() {
  return (
    <PageHeader
      actions={<ButtonLink to={routes.dashboard}>Back to dashboard</ButtonLink>}
      title="Plan details"
      titleId="calculation-title"
    />
  );
}

function LedgerRow({
  emphasis = false,
  label,
  sign,
  value,
}: {
  emphasis?: boolean;
  label: string;
  sign?: "minus" | "plus";
  value: string;
}) {
  return (
    <div className={`ledger-row${emphasis ? " ledger-row-emphasis" : ""}`}>
      <span>{label}</span>
      <strong>
        {sign === "plus" ? "+" : sign === "minus" ? "−" : ""}
        {value}
      </strong>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function SnapshotItemList({
  emptyLabel,
  items,
  kind,
}: {
  emptyLabel: string;
  items: Array<Record<string, JsonValue>>;
  kind: "expense" | "income";
}) {
  if (items.length === 0) {
    return <p className="calculation-detail-copy">{emptyLabel}</p>;
  }

  return (
    <ul className="calculation-detail-list">
      {items.map((item) => {
        const name = getStringValue(item, "name") ?? "Unnamed item";
        const frequency = getStringValue(item, "frequency");
        const nextDate = getStringValue(item, "next_date");
        const amount = getNumberValue(item, "amount_cents");
        const descriptor = [
          frequency === null ? null : frequencyLabel(frequency),
          nextDate === null ? null : formatDate(nextDate),
          kind === "income"
            ? getStringValue(item, "confidence") === "confirmed"
              ? "Confirmed"
              : "Not confirmed"
            : classificationLabel(getStringValue(item, "classification")),
        ]
          .filter((value): value is string => value !== null)
          .join(" · ");

        return (
          <li key={getStringValue(item, "id") ?? name}>
            <span>
              <strong>{name}</strong>
              <small>{descriptor}</small>
            </span>
            <b>{amount === null ? "Not available" : formatCents(amount)}</b>
          </li>
        );
      })}
    </ul>
  );
}

function getJsonObject(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : null;
}

function getObjectArray(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return Array.isArray(value)
    ? value.filter(
        (item): item is Record<string, JsonValue> =>
          item !== null && typeof item === "object" && !Array.isArray(item),
      )
    : [];
}

function getStringArray(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === "string") : [];
}

function getNumberValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return typeof value === "number" ? value : null;
}

function getStringValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return typeof value === "string" ? value : null;
}

function moneyValue(source: Record<string, JsonValue> | null, key: string) {
  const value = getNumberValue(source, key);
  return value === null ? "Not available" : formatCents(value);
}

function numberValue(source: Record<string, JsonValue> | null, key: string, suffix = "") {
  const value = getNumberValue(source, key);
  return value === null ? "Not available" : `${value}${suffix === "" ? "" : ` ${suffix}`}`;
}

function percentValue(source: Record<string, JsonValue> | null, key: string) {
  const value = getNumberValue(source, key);
  return value === null ? "Not available" : formatPercent(value);
}

function dateValue(source: Record<string, JsonValue> | null, key: string) {
  const value = getStringValue(source, key);
  return value === null ? "Not available" : formatDate(value);
}

function statusTone(value: string | null) {
  const normalized = value?.toLowerCase() ?? "";
  if (normalized.includes("risk") || normalized.includes("pace")) {
    return "warning";
  }
  if (normalized === "completed" || normalized === "ahead" || normalized.includes("track")) {
    return "positive";
  }
  return "neutral";
}
