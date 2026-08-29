import type { DashboardPaceSummary, AIExplanationItem } from "../../api/types.ts";
import { Button } from "../ui/Button.tsx";
import { Alert } from "../feedback/Alert.tsx";
import { formatCents, formatDateTime } from "../../utils/format.ts";
import { useAiExplanation } from "../../features/dashboard/useAiExplanation.ts";

type AIExplanationPanelProps = {
  pace: DashboardPaceSummary;
  snapshotId: string;
};

export function AIExplanationPanel({ pace, snapshotId }: AIExplanationPanelProps) {
  const explanation = useAiExplanation();

  const handleRequest = () => {
    void explanation.mutate();
  };

  return (
    <section className="ai-explanation-panel panel" aria-labelledby="ai-explanation-title">
      <div className="ai-explanation-header">
        <div>
          <p className="panel-eyebrow">Optional explanation</p>
          <h2 id="ai-explanation-title">Make sense of this plan</h2>
          <p className="panel-copy">
            Get a short, plain-language read of the plan behind your weekly spending number.
          </p>
        </div>
        {explanation.data?.enabled === false ? null : (
          <Button onClick={handleRequest} disabled={explanation.isPending}>
            {explanation.isPending ? "Preparing explanation" : "Explain this plan"}
          </Button>
        )}
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
  const references = new Set(item.explanation.observations.flatMap((observation) => observation.metric_refs));

  return (
    <div className="ai-explanation-result" data-snapshot-id={snapshotId}>
      <div className="ai-explanation-meta">
        <span>{item.source === "generated" ? "Generated explanation" : "Plan explanation"}</span>
        <span>
          Based on your plan from {formatDateTime(item.calculated_at)} · {item.formula_version}
        </span>
      </div>
      <h3>{item.explanation.headline}</h3>
      <p className="panel-copy">{item.explanation.body}</p>
      {item.explanation.next_step === null ? null : (
        <p className="ai-explanation-next-step">
          <strong>Next step:</strong> {item.explanation.next_step}
        </p>
      )}
      <TrustedMetrics references={references} pace={pace} />
    </div>
  );
}

function TrustedMetrics({
  references,
  pace,
}: {
  references: Set<string>;
  pace: DashboardPaceSummary;
}) {
  const metrics = [
    references.has("pace_status") ? { label: "Plan status", value: pace.pace_status } : null,
    references.has("weekly_safe_to_spend_cents")
      ? { label: "Weekly spending", value: formatCents(pace.weekly_safe_to_spend_cents) }
      : null,
    references.has("projected_shortfall_cents")
      ? { label: "Projected shortfall", value: formatCents(pace.projected_shortfall_cents) }
      : null,
    references.has("progress_percentage")
      ? { label: "Progress", value: `${pace.progress_percentage}%` }
      : null,
    references.has("remaining_weeks")
      ? { label: "Weeks remaining", value: String(pace.remaining_weeks) }
      : null,
  ].filter((metric): metric is { label: string; value: string } => metric !== null);

  if (metrics.length === 0) {
    return null;
  }

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
