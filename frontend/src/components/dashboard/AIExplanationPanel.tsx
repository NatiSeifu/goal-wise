import type { DashboardPaceSummary, AIExplanationItem } from "../../api/types.ts";
import { Button } from "../ui/Button.tsx";
import { Alert } from "../feedback/Alert.tsx";
import { formatCents, formatDateTime } from "../../utils/format.ts";
import {
  useAiExplanation,
  useAiExplanationAvailability,
} from "../../features/dashboard/useAiExplanation.ts";

type AIExplanationPanelProps = {
  pace: DashboardPaceSummary;
  snapshotId: string;
};

export function AIExplanationPanel({ pace, snapshotId }: AIExplanationPanelProps) {
  const availability = useAiExplanationAvailability();

  if (availability.isPending || availability.isError || availability.data?.enabled !== true) {
    return null;
  }

  return <EnabledAIExplanationPanel pace={pace} snapshotId={snapshotId} />;
}

function EnabledAIExplanationPanel({ pace, snapshotId }: AIExplanationPanelProps) {
  const explanation = useAiExplanation();

  const handleRequest = () => {
    void explanation.mutate();
  };

  return (
    <section className="ai-explanation-panel panel" aria-labelledby="ai-explanation-title">
      <div className="ai-explanation-header">
        <div>
          <h2 id="ai-explanation-title">Plan insights</h2>
        </div>
        <Button onClick={handleRequest} disabled={explanation.isPending}>
          {explanation.isPending
            ? "Preparing analysis"
            : explanation.data === undefined
              ? "Generate analysis"
              : "Refresh analysis"}
        </Button>
      </div>

      {explanation.isPending ? (
        <p className="ai-explanation-status" role="status">
          Preparing a summary from your latest plan...
        </p>
      ) : null}

      {explanation.isError ? (
        <Alert title="Explanation unavailable" variant="error">
          <p>{explanation.error instanceof Error ? explanation.error.message : "Try again shortly."}</p>
          <Button className="ai-explanation-retry" onClick={handleRequest}>
            Try again
          </Button>
        </Alert>
      ) : null}

      {explanation.data?.enabled === false ? (
        <p className="ai-explanation-status" role="status">
          Explanations are not enabled in this environment.
        </p>
      ) : null}

      {explanation.data?.enabled === true ? (
        <ExplanationResult
          item={explanation.data.item}
          pace={pace}
          snapshotId={snapshotId}
        />
      ) : null}
    </section>
  );
}

function ExplanationResult({
  item,
  pace,
  snapshotId,
}: {
  item: AIExplanationItem;
  pace: DashboardPaceSummary;
  snapshotId: string;
}) {
  const statusTone = getStatusTone(pace.pace_status);

  return (
    <div className="ai-explanation-result" data-snapshot-id={snapshotId}>
      <div className="ai-explanation-conclusion">
        <div>
          <h3>{item.explanation.headline}</h3>
        </div>
        <span className={`ai-status-badge ${statusTone}`}>{pace.pace_status}</span>
      </div>
      <TrustedMetrics pace={pace} />
      <div className="ai-explanation-copy">
        <p className="ai-explanation-label">What this means</p>
        <p className="panel-copy">{item.explanation.body}</p>
      </div>
      {item.explanation.next_step === null ? null : (
        <div className="ai-explanation-recommendation">
          <p className="ai-explanation-label">Recommended next step</p>
          <p>{item.explanation.next_step}</p>
        </div>
      )}
      <p className="ai-explanation-meta">Analysis based on {formatDateTime(item.calculated_at)}</p>
    </div>
  );
}

function getStatusTone(status: string) {
  if (status === "At Risk" || status === "Off Pace") {
    return "warning";
  }
  if (status === "Completed" || status === "Ahead" || status === "On Track") {
    return "positive";
  }
  return "neutral";
}

function TrustedMetrics({
  pace,
}: {
  pace: DashboardPaceSummary;
}) {
  const metrics = [
    { label: "Weekly spending", value: formatCents(pace.weekly_safe_to_spend_cents) },
    { label: "Progress", value: `${pace.progress_percentage}%` },
    { label: "Projected shortfall", value: formatCents(pace.projected_shortfall_cents) },
  ];

  return (
    <dl className="ai-trusted-metrics" aria-label="Trusted plan values">
      {metrics.map((metric) => (
        <div key={metric.label}>
          <dt>{metric.label}</dt>
          <dd>{metric.value}</dd>
        </div>
      ))}
    </dl>
  );
}
