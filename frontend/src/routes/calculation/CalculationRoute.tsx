import type { JsonValue } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { EmptyState } from "../../components/feedback/EmptyState.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { ButtonLink } from "../../components/ui/Button.tsx";
import { Panel } from "../../components/ui/Panel.tsx";
import { useLatestCalculationSnapshot } from "../../features/snapshots/useLatestCalculationSnapshot.ts";
import { formatDateTime } from "../../utils/format.ts";

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
  const outputs = getJsonObject(snapshot.data.result_json, "outputs");
  const explanation = getJsonObject(snapshot.data.result_json, "explanation");

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

        <Panel title="Output fields">
          <p className="panel-copy">
            These are the backend snapshot output keys currently available for audit and display.
          </p>
          <ul className="key-list">
            {Object.keys(outputs ?? {}).map((key) => (
              <li key={key}>{key}</li>
            ))}
          </ul>
        </Panel>

        <Panel title="Explanation payload">
          <p className="panel-copy">
            The backend stores included and excluded assumption IDs without copying raw transaction descriptions.
          </p>
          <ul className="key-list">
            {Object.keys(explanation ?? {}).map((key) => (
              <li key={key}>{key}</li>
            ))}
          </ul>
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

function getJsonObject(source: Record<string, JsonValue>, key: string) {
  const value = source[key];
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value : null;
}

function getStringValue(source: Record<string, JsonValue> | null, key: string) {
  const value = source?.[key];
  return typeof value === "string" ? value : null;
}
