import { useEffect, useState, type FormEvent } from "react";
import { ApiError, type FieldErrors } from "../../api/errors.ts";
import { archiveGoal, createGoal, updateGoal } from "../../api/resources.ts";
import type { GoalRequest, GoalResponse } from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { FormError } from "../../components/feedback/FormError.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { CoachTip, SetupGuide } from "../../components/onboarding/SetupGuide.tsx";
import { Button, ButtonLink } from "../../components/ui/Button.tsx";
import { TextField } from "../../components/ui/TextField.tsx";
import { useFinancialInputs } from "../../features/financial-inputs/useFinancialInputs.ts";
import { useActiveGoal } from "../../features/goal/useActiveGoal.ts";
import { setupGuideStateFromInputs } from "../../features/setup/setupGuideState.ts";
import { centsToDollarInput, dollarInputToCents, formatCents, formatDate } from "../../utils/format.ts";
import { fieldError, firstFormError } from "../../utils/forms.ts";

type GoalFormState = {
  currentSavedDollars: string;
  initialSavedDollars: string;
  name: string;
  startDate: string;
  targetDate: string;
  targetDollars: string;
};

const emptyGoalForm: GoalFormState = {
  currentSavedDollars: "0.00",
  initialSavedDollars: "0.00",
  name: "",
  startDate: new Date().toISOString().slice(0, 10),
  targetDate: "",
  targetDollars: "",
};

export function GoalRoute() {
  const activeGoal = useActiveGoal();
  const financialInputs = useFinancialInputs();
  const [form, setForm] = useState<GoalFormState>(emptyGoalForm);
  const [fields, setFields] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isArchiving, setIsArchiving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (activeGoal.status === "ready" && activeGoal.data !== null) {
      setForm(goalToForm(activeGoal.data));
    }
  }, [activeGoal.data, activeGoal.status]);

  if (activeGoal.status === "loading") {
    return <RouteLoading fullPage={false} label="Loading active goal" />;
  }

  if (activeGoal.status === "error") {
    return (
      <section className="form-page" aria-labelledby="goal-title">
        <GoalHeader
          title="Goal setup"
          description="Define the one active savings goal supported by the MVP."
        />
        <Alert title="Goal unavailable" variant="error">
          <p>{activeGoal.error}</p>
        </Alert>
      </section>
    );
  }

  const existingGoal = activeGoal.data;
  const guideState = setupGuideStateFromInputs({
    currentStep: "goal",
    expenses: financialInputs.status === "ready" ? financialInputs.data.expenses : [],
    hasGoal: existingGoal !== null,
    incomeSources: financialInputs.status === "ready" ? financialInputs.data.incomeSources : [],
    profile: financialInputs.status === "ready" ? financialInputs.data.profile : null,
  });

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFields({});
    setFormError(null);
    setSuccessMessage(null);
    setIsSubmitting(true);

    try {
      const payload = formToGoalRequest(form);
      const response =
        existingGoal === null ? await createGoal(payload) : await updateGoal(existingGoal.id, payload);
      if (response.item !== null) {
        setForm(goalToForm(response.item));
      }
      setSuccessMessage("Goal saved. Complete the financial inputs to update dashboard results.");
      await activeGoal.reload();
    } catch (error) {
      if (error instanceof ApiError && error.fields !== null) {
        setFields(error.fields);
        setFormError(firstFormError(error.fields));
      } else {
        setFormError(error instanceof Error ? error.message : "Goal could not be saved.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleArchiveGoal() {
    if (existingGoal === null) {
      return;
    }

    setFields({});
    setFormError(null);
    setSuccessMessage(null);
    setIsArchiving(true);

    try {
      await archiveGoal(existingGoal.id);
      setForm(emptyGoalForm);
      setSuccessMessage("Goal archived. Its prior calculations remain saved, and you can create a new active goal.");
      await activeGoal.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Goal could not be archived.");
    } finally {
      setIsArchiving(false);
    }
  }

  return (
    <section className="form-page" aria-labelledby="goal-title">
      <GoalHeader
        title="Goal setup"
        description="Create or update the savings goal used for your weekly plan."
      />
      <SetupGuide
        activeStep={guideState.activeStep}
        completedSteps={guideState.completedSteps}
        compact={existingGoal !== null}
      />

      {existingGoal === null ? null : (
        <div className="summary-strip" aria-label="Current active goal summary">
          <span>{existingGoal.name}</span>
          <span>{formatCents(existingGoal.current_saved_cents)} saved</span>
          <span>{formatDate(existingGoal.target_date)}</span>
        </div>
      )}

      <form className="form-panel" onSubmit={(event) => void handleSubmit(event)}>
        <FormError message={formError} />
        {successMessage === null ? null : (
          <p className="form-success" role="status">
            {successMessage}
          </p>
        )}
        <div className="form-grid">
          <TextField
            error={fieldError(fields, "name")}
            id="goal-name"
            label="Goal name"
            maxLength={120}
            onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
            required
            type="text"
            value={form.name}
          />
          <TextField
            error={fieldError(fields, "target_cents")}
            id="goal-target"
            label="Target amount"
            min="0"
            onChange={(event) => setForm((current) => ({ ...current, targetDollars: event.target.value }))}
            required
            step="0.01"
            type="number"
            value={form.targetDollars}
          />
          <TextField
            error={fieldError(fields, "initial_saved_cents")}
            id="goal-initial-saved"
            label="Initial saved"
            min="0"
            onChange={(event) =>
              setForm((current) => ({ ...current, initialSavedDollars: event.target.value }))
            }
            required
            step="0.01"
            type="number"
            value={form.initialSavedDollars}
          />
          <TextField
            error={fieldError(fields, "current_saved_cents")}
            id="goal-current-saved"
            label="Current saved"
            min="0"
            onChange={(event) =>
              setForm((current) => ({ ...current, currentSavedDollars: event.target.value }))
            }
            required
            step="0.01"
            type="number"
            value={form.currentSavedDollars}
          />
          <TextField
            error={fieldError(fields, "start_date")}
            id="goal-start-date"
            label="Start date"
            onChange={(event) => setForm((current) => ({ ...current, startDate: event.target.value }))}
            required
            type="date"
            value={form.startDate}
          />
          <TextField
            error={fieldError(fields, "target_date")}
            id="goal-target-date"
            label="Target date"
            onChange={(event) => setForm((current) => ({ ...current, targetDate: event.target.value }))}
            required
            type="date"
            value={form.targetDate}
          />
        </div>
        <div className="form-actions">
          <Button disabled={isSubmitting || isArchiving} type="submit">
            {isSubmitting ? "Saving goal" : existingGoal === null ? "Create goal" : "Save goal"}
          </Button>
          {existingGoal === null ? null : (
            <Button
              disabled={isSubmitting || isArchiving}
              onClick={() => void handleArchiveGoal()}
              type="button"
              variant="danger"
            >
              {isArchiving ? "Archiving goal" : "Archive active goal"}
            </Button>
          )}
          <ButtonLink to={routes.financialInputs}>
            Continue to inputs
          </ButtonLink>
          <ButtonLink to={routes.dashboard}>
            View dashboard
          </ButtonLink>
        </div>
        {existingGoal === null ? null : (
          <p className="form-help">
            Archiving removes this goal from active planning without deleting its saved calculation history.
          </p>
        )}
      </form>
      <CoachTip title="What this controls">
        The goal sets the deadline and savings gap. After this, add cash, income, and planned expenses.
      </CoachTip>
    </section>
  );
}

function GoalHeader({ description, title }: { description: string; title: string }) {
  return (
    <PageHeader description={description} title={title} titleId="goal-title" />
  );
}

function goalToForm(goal: GoalResponse): GoalFormState {
  return {
    currentSavedDollars: centsToDollarInput(goal.current_saved_cents),
    initialSavedDollars: centsToDollarInput(goal.initial_saved_cents),
    name: goal.name,
    startDate: goal.start_date,
    targetDate: goal.target_date,
    targetDollars: centsToDollarInput(goal.target_cents),
  };
}

function formToGoalRequest(form: GoalFormState): GoalRequest {
  return {
    current_saved_cents: dollarInputToCents(form.currentSavedDollars),
    initial_saved_cents: dollarInputToCents(form.initialSavedDollars),
    name: form.name,
    start_date: form.startDate,
    target_cents: dollarInputToCents(form.targetDollars),
    target_date: form.targetDate,
  };
}
