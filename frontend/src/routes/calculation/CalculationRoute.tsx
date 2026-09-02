import type { JsonValue } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { EmptyState } from "../../components/feedback/EmptyState.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { ButtonLink } from "../../components/ui/Button.tsx";
import { Panel } from "../../components/ui/Panel.tsx";
import { useLatestCalculationSnapshot } from "../../features/snapshots/useLatestCalculationSnapshot.ts";
import { formatCents, formatDateTime, formatPercent } from "../../utils/format.ts";
import { paceStatusDescription, paceStatusLabel } from "../../utils/labels.ts";

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

  const incomeSources = getArrayValue(snapshot.data.normalized_input_json, "income_sources");
  const plannedExpenses = getArrayValue(snapshot.data.normalized_input_json, "planned_expenses");
  const outputs = getJsonObject(snapshot.data.result_json, "outputs");
  const explanation = getJsonObject(snapshot.data.result_json, "explanation");
  const explanationSummary = getJsonObject(explanation, "summary");
  const paceStatus = getStringValue(outputs, "pace_status");

  return (
    <section className="dashboard-page" aria-labelledby="calculation-title">
      <CalculationHeader />
      <p className="calculation-meta">Last calculated {formatDateTime(snapshot.data.calculated_at)}</p>
      <section className="calculation-layout" aria-label="Plan details">
        <Panel className="calculation-plan" title="Your current plan">
          <dl className="metric-list compact calculation-metrics">
            <SnapshotMoneyValue label="Weekly safe-to-spend" outputs={outputs} field="weekly_safe_to_spend_cents" />
            <SnapshotStatusValue outputs={outputs} />
            <SnapshotMoneyValue label="Projected shortfall" outputs={outputs} field="projected_shortfall_cents" />
            <SnapshotNumberValue label="Remaining weeks" outputs={outputs} field="remaining_weeks" />
            <SnapshotPercentValue label="Progress" outputs={outputs} field="progress_percentage" />
          </dl>
          {paceStatus === null ? null : (
            <p className="calculation-status-note">{paceStatusDescription(paceStatus)}</p>
          )}
        </Panel>

        <Panel title="Included in this plan">
          <p className="panel-copy">
            These saved assumptions were used to calculate your current weekly plan.
          </p>
          <dl className="calculation-input-summary">
            <div>
              <dt>Income sources</dt>
              <dd>{incomeSources.length}</dd>
            </div>
            <div>
              <dt>Planned expenses</dt>
              <dd>{plannedExpenses.length}</dd>
            </div>
            <div>
              <dt>Confirmed income</dt>
              <dd>{getNumberValue(explanationSummary, "confirmed_income_count") ?? "0"}</dd>
            </div>
            <div>
              <dt>Unconfirmed income</dt>
              <dd>{getNumberValue(explanationSummary, "unconfirmed_income_count") ?? "0"}</dd>
            </div>
          </dl>
        </Panel>
      </section>
    </section>
  );
}

function CalculationHeader() {
  return (
    <PageHeader
      actions={
        <ButtonLink to={routes.dashboard}>
          Back to dashboard
        </ButtonLink>
      }
      description="A plain-language view of the numbers behind your current weekly plan."
      title="Plan details"
      titleId="calculation-title"
    />
  );
}

function getJsonObject(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : null;
}

function getArrayValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return Array.isArray(value) ? value : [];
}

function getNumberValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return typeof value === "number" ? value : null;
}

function getStringValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return typeof value === "string" ? value : null;
}

function SnapshotMoneyValue({
  field,
  label,
  outputs,
}: {
  field: string;
  label: string;
  outputs: Record<string, JsonValue> | null;
}) {
  const value = getNumberValue(outputs, field);
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value === null ? "Not available" : formatCents(value)}</dd>
    </div>
  );
}

function SnapshotNumberValue({
  field,
  label,
  outputs,
}: {
  field: string;
  label: string;
  outputs: Record<string, JsonValue> | null;
}) {
  const value = getNumberValue(outputs, field);
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value ?? "Not available"}</dd>
    </div>
  );
}

function SnapshotPercentValue({
  field,
  label,
  outputs,
}: {
  field: string;
  label: string;
  outputs: Record<string, JsonValue> | null;
}) {
  const value = getNumberValue(outputs, field);
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value === null ? "Not available" : formatPercent(value)}</dd>
    </div>
  );
}

function SnapshotStatusValue({ outputs }: { outputs: Record<string, JsonValue> | null }) {
  const value = getStringValue(outputs, "pace_status");
  return (
    <div>
      <dt>Plan status</dt>
      <dd>{value === null ? "Not available" : paceStatusLabel(value)}</dd>
    </div>
  );
}
