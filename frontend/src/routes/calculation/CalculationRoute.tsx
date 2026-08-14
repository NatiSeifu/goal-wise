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

export function CalculationRoute() {
  const snapshot = useLatestCalculationSnapshot();

  if (snapshot.status === "loading") {
    return <RouteLoading fullPage={false} label="Loading calculation details" />;
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
          title="No snapshot yet"
          description="Save a valid goal and financial assumptions before viewing calculation details."
          action={
            <ButtonLink variant="primary" to={routes.financialInputs}>
              Open financial inputs
            </ButtonLink>
          }
        />
      </section>
    );
  }

  const calculation = getJsonObject(snapshot.data.normalized_input_json, "calculation");
  const incomeSources = getArrayValue(snapshot.data.normalized_input_json, "income_sources");
  const plannedExpenses = getArrayValue(snapshot.data.normalized_input_json, "planned_expenses");
  const outputs = getJsonObject(snapshot.data.result_json, "outputs");
  const explanation = getJsonObject(snapshot.data.result_json, "explanation");
  const explanationSummary = getJsonObject(explanation, "summary");

  return (
    <section className="dashboard-page" aria-labelledby="calculation-title">
      <CalculationHeader />
      <section className="dashboard-grid" aria-label="Calculation snapshot">
        <Panel title="Snapshot">
          <dl className="snapshot-list">
            <div>
              <dt>ID</dt>
              <dd>{snapshot.data.id}</dd>
            </div>
            <div>
              <dt>Formula version</dt>
              <dd>{snapshot.data.formula_version}</dd>
            </div>
            <div>
              <dt>Trigger</dt>
              <dd>{getStringValue(calculation, "trigger") ?? snapshot.data.trigger}</dd>
            </div>
            <div>
              <dt>Calculated</dt>
              <dd>{formatDateTime(snapshot.data.calculated_at)}</dd>
            </div>
          </dl>
        </Panel>

        <Panel title="Pace result">
          <dl className="metric-list compact">
            <SnapshotMoneyValue label="Weekly safe-to-spend" outputs={outputs} field="weekly_safe_to_spend_cents" />
            <SnapshotTextValue label="Pace status" outputs={outputs} field="pace_status" />
            <SnapshotMoneyValue label="Projected shortfall" outputs={outputs} field="projected_shortfall_cents" />
            <SnapshotNumberValue label="Remaining weeks" outputs={outputs} field="remaining_weeks" />
            <SnapshotPercentValue label="Progress" outputs={outputs} field="progress_percentage" />
          </dl>
        </Panel>

        <Panel title="Normalized inputs">
          <p className="panel-copy">
            This snapshot stores the validated inputs used by the deterministic engine. It is read-only.
          </p>
          <dl className="metric-list compact">
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
      description="Latest immutable snapshot returned by the backend."
      title="Calculation details"
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

function SnapshotTextValue({
  field,
  label,
  outputs,
}: {
  field: string;
  label: string;
  outputs: Record<string, JsonValue> | null;
}) {
  const value = getStringValue(outputs, field);
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value ?? "Not available"}</dd>
    </div>
  );
}
