import { Link } from "react-router-dom";
import type { DashboardPaceSummary, AIExplanationItem, AIObservation } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Button } from "../ui/Button.tsx";
import { formatCents, formatDateTime, formatPercent } from "../../utils/format.ts";
import { paceStatusLabel } from "../../utils/labels.ts";
import {
  useAiExplanation,
  useAiExplanationAvailability,
} from "../../features/dashboard/useAiExplanation.ts";

type AIExplanationPanelProps = {
  pace: DashboardPaceSummary;
  snapshotId: string;
};

const observationLabels: Record<AIObservation["kind"], string> = {
  pace: "Savings pace",
  allowance: "Spending room",
  progress: "Goal progress",
  shortfall: "Goal outlook",
};

export function AIExplanationPanel(props: AIExplanationPanelProps) {
  const availability = useAiExplanationAvailability();
  if (availability.isPending || availability.isError || availability.data?.enabled !== true) {
    return null;
  }
  return <EnabledAIExplanationPanel {...props} />;
}

function EnabledAIExplanationPanel({ pace, snapshotId }: AIExplanationPanelProps) {
  const explanation = useAiExplanation();
  const item = explanation.data?.enabled === true ? explanation.data.item : null;
  // A plan can change while generation is in flight. Never pair an older digest
  // (or a newer response from another tab) with this dashboard's numbers.
  const isCurrent = item !== null && item.snapshot_id === snapshotId;
  const handleRequest = () => void explanation.mutate();

  return (
    <section className="ai-digest" aria-labelledby="ai-digest-title" aria-busy={explanation.isPending}>
      <header className="ai-digest-header">
        <div className="ai-digest-title">
          <span className="ai-digest-mark" aria-hidden="true">AI</span>
          <h2 id="ai-digest-title">Plan digest</h2>
        </div>
        <Button variant="secondary" onClick={handleRequest} disabled={explanation.isPending}>
          {explanation.isPending ? "Writing digest…" : isCurrent ? "Read again" : "Generate digest"}
        </Button>
      </header>

      {explanation.isPending ? (
        <div className="ai-digest-loading" role="status">
          <p>Reading your savings pace, spending room, and goal outlook…</p>
          <div className="ai-digest-skeleton" aria-hidden="true"><span /><span /><span /></div>
        </div>
      ) : explanation.isError ? (
        <div className="ai-digest-error" role="alert">
          <h3>Digest unavailable</h3>
          <p>{explanation.error instanceof Error ? explanation.error.message : "Please try again."}</p>
          <Button variant="secondary" onClick={handleRequest}>Try again</Button>
        </div>
      ) : item !== null && !isCurrent ? (
        <p className="ai-digest-empty" role="status">Your plan changed. Reload the dashboard to read the latest digest.</p>
      ) : isCurrent ? (
        <ExplanationResult item={item} pace={pace} />
      ) : (
        <p className="ai-digest-empty">
          {explanation.data?.enabled === false
            ? "AI digest is unavailable."
            : "Your savings pace, spending room, and what to review next."}
        </p>
      )}
    </section>
  );
}

function ExplanationResult({ item, pace }: { item: AIExplanationItem; pace: DashboardPaceSummary }) {
  const { explanation } = item;
  const reviewGoal = explanation.next_step_action === "review_goal";

  return (
    <div className="ai-digest-result" data-snapshot-id={item.snapshot_id}>
      <div className="ai-digest-overview">
        <h3>{explanation.headline}</h3>
        <p>{explanation.body}</p>
      </div>
      <div className="ai-digest-observations">
        {explanation.observations.map((observation) => (
          <section className="ai-digest-observation" key={observation.kind} aria-label={observationLabels[observation.kind]}>
            <h4><span className={`ai-digest-signal ${observation.tone}`} aria-hidden="true" />{observationLabels[observation.kind]}</h4>
            <p>{observation.text}</p>
            <dl className="ai-digest-evidence">
              {observation.metric_refs.map((reference) => {
                const metric = trustedMetric(reference, pace, item.formula_version);
                return metric === null ? null : <div key={reference}><dt>{metric.label}</dt><dd>{metric.value}</dd></div>;
              })}
            </dl>
          </section>
        ))}
      </div>
      <div className="ai-digest-next">
        <div>
          <h4>What to do next</h4>
          <p>{explanation.next_step}</p>
        </div>
        <Link className="button" to={reviewGoal ? routes.goal : routes.financialInputs}>
          {reviewGoal ? "Review goal" : "Review inputs"}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>
        </Link>
      </div>
      <p className="ai-digest-meta">AI-generated · Plan calculated {formatDateTime(item.calculated_at)} · {item.formula_version}</p>
    </div>
  );
}

function trustedMetric(reference: string, pace: DashboardPaceSummary, formulaVersion: string) {
  const metrics: Record<string, { label: string; value: string }> = {
    pace_status: { label: "Status", value: paceStatusLabel(pace.pace_status) },
    weekly_safe_to_spend_cents: { label: "Weekly spending", value: formatCents(pace.weekly_safe_to_spend_cents) },
    projected_shortfall_cents: { label: "Shortfall", value: formatCents(pace.projected_shortfall_cents) },
    progress_percentage: { label: "Saved", value: formatPercent(pace.progress_percentage) },
    remaining_weeks: { label: "Time left", value: `${pace.remaining_weeks} weeks` },
    formula_version: { label: "Calculation", value: formulaVersion },
  };
  return metrics[reference] ?? null;
}
