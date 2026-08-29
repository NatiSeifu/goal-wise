import { useState, type ChangeEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { ApiError, type ApiIssue } from "../../api/errors.ts";
import { queryKeys } from "../../api/queryKeys.ts";
import { confirmPlanningImport, previewPlanningImport } from "../../api/resources.ts";
import type { PlanningImportPreviewResponse, PlanningImportSourcePreview } from "../../api/types.ts";
import { FormError } from "../../components/feedback/FormError.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { Button } from "../../components/ui/Button.tsx";
import { formatCents, formatDate } from "../../utils/format.ts";

export function PlanningImportRoute() {
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<PlanningImportPreviewResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<"preview" | "confirm" | null>(null);

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    setPreview(null);
    setError(null);
    setSuccessMessage(null);
  }

  async function handlePreview() {
    if (selectedFile === null) {
      return;
    }

    setBusyAction("preview");
    setError(null);
    setSuccessMessage(null);
    try {
      setPreview(await previewPlanningImport(selectedFile));
    } catch (caughtError) {
      setError(toApiError(caughtError, "The file could not be reviewed."));
    } finally {
      setBusyAction(null);
    }
  }

  async function handleConfirm() {
    if (preview === null) {
      return;
    }

    setBusyAction("confirm");
    setError(null);
    setSuccessMessage(null);
    try {
      await confirmPlanningImport(preview.preview_token);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.activeGoal }),
        queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
        queryClient.invalidateQueries({ queryKey: queryKeys.financialInputs }),
        queryClient.invalidateQueries({ queryKey: queryKeys.latestCalculationSnapshot }),
      ]);
      setSuccessMessage("Your plan was imported. The dashboard now reflects these values.");
      setPreview(null);
      setSelectedFile(null);
    } catch (caughtError) {
      setError(toApiError(caughtError, "The plan could not be imported."));
    } finally {
      setBusyAction(null);
    }
  }

  const isBusy = busyAction !== null;
  return (
    <section className="form-page wide" aria-labelledby="planning-import-title">
      <PageHeader
        description="Bring in one complete GoalWise plan from a prepared CSV file."
        title="Import a plan"
        titleId="planning-import-title"
      />

      <div className="import-intro">
        <div>
          <h2>Review before anything changes</h2>
          <p>
            This file sets one goal, your cash position, expected income, and planned expenses. It is not a bank statement.
            Importing replaces the current active plan after you confirm it.
          </p>
        </div>
        <a href="/planning-import-template.csv" download>
          Download CSV template
        </a>
      </div>

      <div className="form-panel import-panel">
        <div className="import-file-picker">
          <label htmlFor="planning-import-file">GoalWise planning CSV</label>
          <input
            accept=".csv,text/csv"
            id="planning-import-file"
            onChange={(event) => void handleFileChange(event)}
            type="file"
          />
          <p className="form-help">
            Use the canonical columns and decimal dollar amounts. Your file is checked before it can change your plan.
          </p>
        </div>
        <FormError message={error?.message ?? null} />
        {error?.issues.length ? <ImportIssues issues={error.issues} /> : null}
        {successMessage === null ? null : <p className="form-success" role="status">{successMessage}</p>}
        <div className="form-actions">
          <Button disabled={selectedFile === null || isBusy} type="button" onClick={() => void handlePreview()}>
            {busyAction === "preview" ? "Reviewing file" : "Review file"}
          </Button>
          {selectedFile === null ? null : <span className="selected-file">{selectedFile.name}</span>}
        </div>
      </div>

      {preview === null ? null : <ImportPreview preview={preview} isBusy={isBusy} onConfirm={() => void handleConfirm()} />}
    </section>
  );
}

function ImportPreview({
  preview,
  isBusy,
  onConfirm,
}: {
  preview: PlanningImportPreviewResponse;
  isBusy: boolean;
  onConfirm: () => void;
}) {
  return (
    <section className="form-panel import-preview" aria-labelledby="import-preview-title">
      <div className="section-heading-row">
        <div>
          <h2 id="import-preview-title">Ready to import</h2>
          <p>{preview.row_count} rows reviewed. Confirming will replace the current active plan.</p>
        </div>
        <span className="import-validity">Valid plan</span>
      </div>
      <div className="import-summary-grid">
        <SummaryItem label="Goal" value={preview.goal.name} detail={`${formatCents(preview.goal.target_cents)} by ${formatDate(preview.goal.target_date)}`} />
        <SummaryItem label="Saved now" value={formatCents(preview.goal.current_saved_cents)} detail={`Started at ${formatCents(preview.goal.initial_saved_cents)}`} />
        <SummaryItem label="Cash available" value={formatCents(preview.cash.starting_cash_cents)} detail={`As of ${formatDate(preview.cash.balance_as_of_date)}`} />
        <SummaryItem label="Protected reserve" value={formatCents(preview.cash.reserve_buffer_cents)} detail={`${preview.income_sources.length} income · ${preview.planned_expenses.length} expenses`} />
      </div>
      <ImportSourceTable title="Expected income" items={preview.income_sources} kind="income" />
      <ImportSourceTable title="Planned expenses" items={preview.planned_expenses} kind="expense" />
      <div className="import-confirmation">
        <p>Only confirm when these values match the plan you want GoalWise to use.</p>
        <Button disabled={isBusy} type="button" onClick={onConfirm}>
          {isBusy ? "Importing plan" : "Confirm import"}
        </Button>
      </div>
    </section>
  );
}

function SummaryItem({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <div className="import-summary-item"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>;
}

function ImportSourceTable({ title, items, kind }: { title: string; items: PlanningImportSourcePreview[]; kind: "income" | "expense" }) {
  return (
    <div className="import-table-section">
      <h3>{title}</h3>
      {items.length === 0 ? <p className="form-help">None in this file.</p> : (
        <div className="import-table-wrap">
          <table>
            <thead><tr><th scope="col">Name</th><th scope="col">Amount</th><th scope="col">Next date</th><th scope="col">Frequency</th><th scope="col">{kind === "income" ? "Confidence" : "Type"}</th></tr></thead>
            <tbody>{items.map((item) => <tr key={`${kind}-${item.name}-${item.next_date}`}><th scope="row">{item.name}</th><td>{formatCents(item.amount_cents)}</td><td>{formatDate(item.next_date)}</td><td>{item.frequency}</td><td>{kind === "income" ? item.confidence : item.classification}</td></tr>)}</tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function ImportIssues({ issues }: { issues: ApiIssue[] }) {
  return <ul className="import-issues">{issues.map((issue) => <li key={`${issue.row}-${issue.field}-${issue.code}`}><strong>Row {issue.row}, {issue.field}:</strong> {issue.message}</li>)}</ul>;
}

function toApiError(value: unknown, fallback: string) {
  if (value instanceof ApiError) {
    return value;
  }
  return new ApiError({ status: 0, code: "request_failed", message: value instanceof Error ? value.message : fallback });
}
