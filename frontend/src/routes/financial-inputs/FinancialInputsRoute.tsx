import { useEffect, useState, type FormEvent } from "react";
import { useQueryClient, type QueryClient } from "@tanstack/react-query";
import { useLocation } from "react-router-dom";
import { ApiError, type FieldErrors } from "../../api/errors.ts";
import { queryKeys } from "../../api/queryKeys.ts";
import {
  createIncomeSource,
  createPlannedExpense,
  deleteIncomeSource,
  deletePlannedExpense,
  putFinancialProfile,
  updateIncomeSource,
  updatePlannedExpense,
} from "../../api/resources.ts";
import type {
  FinancialProfileRequest,
  FinancialProfileResponse,
  IncomeSourceRequest,
  IncomeSourceResponse,
  PlannedExpenseRequest,
  PlannedExpenseResponse,
} from "../../api/types.ts";
import { routes } from "../../app/routes.ts";
import { Alert } from "../../components/feedback/Alert.tsx";
import { FormError } from "../../components/feedback/FormError.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { PageHeader } from "../../components/layout/PageHeader.tsx";
import { CoachTip, SetupGuide } from "../../components/onboarding/SetupGuide.tsx";
import { Button, ButtonLink } from "../../components/ui/Button.tsx";
import { SelectField } from "../../components/ui/SelectField.tsx";
import { TextField } from "../../components/ui/TextField.tsx";
import { useFinancialInputs } from "../../features/financial-inputs/useFinancialInputs.ts";
import { useActiveGoal } from "../../features/goal/useActiveGoal.ts";
import { setupGuideStateFromInputs } from "../../features/setup/setupGuideState.ts";
import {
  centsToDollarInput,
  dollarInputToCents,
  formatCents,
  formatDate,
} from "../../utils/format.ts";
import { fieldError, firstFormError } from "../../utils/forms.ts";
import { classificationLabel, confidenceLabel, frequencyLabel } from "../../utils/labels.ts";

type ProfileFormState = {
  balanceAsOfDate: string;
  reserveBufferConfirmed: boolean;
  reserveBufferDollars: string;
  startingCashDollars: string;
};

type IncomeFormState = {
  amountDollars: string;
  confidence: string;
  frequency: string;
  name: string;
  nextDate: string;
};

type ExpenseFormState = {
  amountDollars: string;
  classification: string;
  frequency: string;
  name: string;
  nextDate: string;
};

const frequencyOptions = [
  { label: frequencyLabel("one_time"), value: "one_time" },
  { label: frequencyLabel("weekly"), value: "weekly" },
  { label: frequencyLabel("biweekly"), value: "biweekly" },
  { label: frequencyLabel("monthly"), value: "monthly" },
];

const confidenceOptions = [
  { label: confidenceLabel("confirmed"), value: "confirmed" },
  { label: confidenceLabel("unconfirmed"), value: "unconfirmed" },
];

const classificationOptions = [
  { label: classificationLabel("essential"), value: "essential" },
  { label: classificationLabel("discretionary"), value: "discretionary" },
];

const emptyProfileForm: ProfileFormState = {
  balanceAsOfDate: new Date().toISOString().slice(0, 10),
  reserveBufferConfirmed: false,
  reserveBufferDollars: "0.00",
  startingCashDollars: "0.00",
};

const emptyIncomeForm: IncomeFormState = {
  amountDollars: "",
  confidence: "confirmed",
  frequency: "monthly",
  name: "",
  nextDate: new Date().toISOString().slice(0, 10),
};

const emptyExpenseForm: ExpenseFormState = {
  amountDollars: "",
  classification: "essential",
  frequency: "monthly",
  name: "",
  nextDate: new Date().toISOString().slice(0, 10),
};

export function FinancialInputsRoute() {
  const queryClient = useQueryClient();
  const inputs = useFinancialInputs();
  const activeGoal = useActiveGoal();
  const location = useLocation();
  const [profileForm, setProfileForm] = useState<ProfileFormState>(emptyProfileForm);
  const [incomeForm, setIncomeForm] = useState<IncomeFormState>(emptyIncomeForm);
  const [expenseForm, setExpenseForm] = useState<ExpenseFormState>(emptyExpenseForm);
  const [editingIncomeId, setEditingIncomeId] = useState<string | null>(null);
  const [editingExpenseId, setEditingExpenseId] = useState<string | null>(null);
  const [profileFields, setProfileFields] = useState<FieldErrors>({});
  const [incomeFields, setIncomeFields] = useState<FieldErrors>({});
  const [expenseFields, setExpenseFields] = useState<FieldErrors>({});
  const [profileError, setProfileError] = useState<string | null>(null);
  const [incomeError, setIncomeError] = useState<string | null>(null);
  const [expenseError, setExpenseError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const isBusy = busyAction !== null;

  useEffect(() => {
    if (inputs.status === "ready" && inputs.data.profile !== null) {
      setProfileForm(profileToForm(inputs.data.profile));
    }
  }, [inputs.data, inputs.status]);

  useEffect(() => {
    if (inputs.status !== "ready" || location.hash === "") {
      return;
    }

    window.requestAnimationFrame(() => {
      document.getElementById(location.hash.slice(1))?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }, [inputs.status, location.hash]);

  if (inputs.status === "loading" || activeGoal.status === "loading") {
    return <RouteLoading fullPage={false} label="Loading financial inputs" />;
  }

  if (inputs.status === "error" || activeGoal.status === "error") {
    const error = inputs.status === "error" ? inputs.error : activeGoal.error;

    return (
      <section className="form-page" aria-labelledby="financial-inputs-title">
        <RouteHeader />
        <Alert title="Financial inputs unavailable" variant="error">
          <p>{error}</p>
        </Alert>
      </section>
    );
  }

  async function reloadAfterSuccess(message: string) {
    setSuccessMessage(message);
    await invalidateFinancialPlanningQueries(queryClient);
  }

  async function handleProfileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setProfileFields({});
    setProfileError(null);
    setSuccessMessage(null);
    setBusyAction("profile");
    try {
      const response = await putFinancialProfile(formToProfileRequest(profileForm));
      if (response.item !== null) {
        setProfileForm(profileToForm(response.item));
      }
      await reloadAfterSuccess("Cash picture saved. Open the dashboard to view your weekly plan.");
    } catch (error) {
      handleFormError(error, setProfileFields, setProfileError, "Cash picture could not be saved.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleIncomeSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIncomeFields({});
    setIncomeError(null);
    setSuccessMessage(null);
    setBusyAction("income");
    try {
      const payload = formToIncomeRequest(incomeForm);
      if (editingIncomeId === null) {
        await createIncomeSource(payload);
      } else {
        await updateIncomeSource(editingIncomeId, payload);
      }
      resetIncomeForm();
      await reloadAfterSuccess("Income source saved.");
    } catch (error) {
      handleFormError(error, setIncomeFields, setIncomeError, "Income source could not be saved.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleExpenseSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setExpenseFields({});
    setExpenseError(null);
    setSuccessMessage(null);
    setBusyAction("expense");
    try {
      const payload = formToExpenseRequest(expenseForm);
      if (editingExpenseId === null) {
        await createPlannedExpense(payload);
      } else {
        await updatePlannedExpense(editingExpenseId, payload);
      }
      resetExpenseForm();
      await reloadAfterSuccess("Planned expense saved.");
    } catch (error) {
      handleFormError(error, setExpenseFields, setExpenseError, "Planned expense could not be saved.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleDeactivateIncome(incomeSourceId: string) {
    setBusyAction(`income-${incomeSourceId}`);
    setSuccessMessage(null);
    try {
      await deleteIncomeSource(incomeSourceId);
      if (editingIncomeId === incomeSourceId) {
        resetIncomeForm();
      }
      await reloadAfterSuccess("Income source removed from this plan.");
    } catch (error) {
      setIncomeError(error instanceof Error ? error.message : "Income source could not be removed from this plan.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleDeactivateExpense(expenseId: string) {
    setBusyAction(`expense-${expenseId}`);
    setSuccessMessage(null);
    try {
      await deletePlannedExpense(expenseId);
      if (editingExpenseId === expenseId) {
        resetExpenseForm();
      }
      await reloadAfterSuccess("Planned expense removed from this plan.");
    } catch (error) {
      setExpenseError(error instanceof Error ? error.message : "Planned expense could not be removed from this plan.");
    } finally {
      setBusyAction(null);
    }
  }

  function resetIncomeForm() {
    setEditingIncomeId(null);
    setIncomeForm(emptyIncomeForm);
    setIncomeFields({});
    setIncomeError(null);
  }

  function resetExpenseForm() {
    setEditingExpenseId(null);
    setExpenseForm(emptyExpenseForm);
    setExpenseFields({});
    setExpenseError(null);
  }

  function startIncomeEdit(item: IncomeSourceResponse) {
    setSuccessMessage(null);
    setIncomeFields({});
    setIncomeError(null);
    setEditingIncomeId(item.id);
    setIncomeForm(incomeToForm(item));
  }

  function startExpenseEdit(item: PlannedExpenseResponse) {
    setSuccessMessage(null);
    setExpenseFields({});
    setExpenseError(null);
    setEditingExpenseId(item.id);
    setExpenseForm(expenseToForm(item));
  }

  const hasGoal = activeGoal.data !== null;
  const guideState = setupGuideStateFromInputs({
    currentStep: "profile",
    expenses: inputs.data.expenses,
    hasGoal,
    incomeSources: inputs.data.incomeSources,
    profile: inputs.data.profile,
  });

  return (
    <section className="form-page wide" aria-labelledby="financial-inputs-title">
      <RouteHeader />
      <SetupGuide activeStep={guideState.activeStep} completedSteps={guideState.completedSteps} />
      {successMessage === null ? null : (
        <p className="form-success" role="status">
          {successMessage}
        </p>
      )}

      <form className="form-panel" id="cash-picture" onSubmit={(event) => void handleProfileSubmit(event)}>
        <div className="section-heading-row">
          <div>
            <h2>Cash picture</h2>
            <p>Start with the money available today and the reserve you want protected.</p>
          </div>
        </div>
        <FormError message={profileError} />
        <div className="cash-picture-fields">
          <TextField
            error={fieldError(profileFields, "starting_cash_cents")}
            id="profile-starting-cash"
            description="Cash outside goal savings. Do not include current saved here."
            label="Starting cash"
            min="0"
            onChange={(event) =>
              setProfileForm((current) => ({ ...current, startingCashDollars: event.target.value }))
            }
            required
            step="0.01"
            type="number"
            value={profileForm.startingCashDollars}
          />
          <TextField
            error={fieldError(profileFields, "balance_as_of_date")}
            id="profile-balance-date"
            label="Balance as of"
            onChange={(event) =>
              setProfileForm((current) => ({ ...current, balanceAsOfDate: event.target.value }))
            }
            required
            type="date"
            value={profileForm.balanceAsOfDate}
          />
          <div className="reserve-field">
            <TextField
              error={fieldError(profileFields, "reserve_buffer_cents")}
              id="profile-reserve-buffer"
              label="Reserve buffer"
              min="0"
              onChange={(event) =>
                setProfileForm((current) => ({ ...current, reserveBufferDollars: event.target.value }))
              }
              required
              step="0.01"
              type="number"
              value={profileForm.reserveBufferDollars}
            />
            <label className="reserve-confirmation" htmlFor="profile-reserve-confirmed">
              <input
                checked={profileForm.reserveBufferConfirmed}
                id="profile-reserve-confirmed"
                onChange={(event) =>
                  setProfileForm((current) => ({ ...current, reserveBufferConfirmed: event.target.checked }))
                }
                type="checkbox"
              />
              <span>
                <strong>Protect this reserve</strong>
                <small>Keep this amount outside weekly spending.</small>
              </span>
            </label>
          </div>
        </div>
        <div className="form-actions">
          <Button disabled={isBusy} type="submit">
            {busyAction === "profile" ? "Saving cash picture" : "Save cash picture"}
          </Button>
        </div>
      </form>
      <CoachTip title="Reserve buffer">
        Keep this as money you want excluded from spending guidance. GoalWise will not silently change it after you confirm it.
      </CoachTip>

      <section className="input-section-grid">
        <form className="form-panel" id="income-sources" onSubmit={(event) => void handleIncomeSubmit(event)}>
          <div className="section-heading-row">
            <div>
              <h2>{editingIncomeId === null ? "Add income source" : "Edit income source"}</h2>
              <p>Use confirmed for money you are comfortable counting on before the goal date.</p>
            </div>
          </div>
          <FormError message={incomeError} />
          <div className="source-fields">
            <SourceFields
              amountDollars={incomeForm.amountDollars}
              fields={incomeFields}
              frequency={incomeForm.frequency}
              name={incomeForm.name}
              nextDate={incomeForm.nextDate}
              prefix="income"
              onAmountChange={(amountDollars) => setIncomeForm((current) => ({ ...current, amountDollars }))}
              onFrequencyChange={(frequency) => setIncomeForm((current) => ({ ...current, frequency }))}
              onNameChange={(name) => setIncomeForm((current) => ({ ...current, name }))}
              onNextDateChange={(nextDate) => setIncomeForm((current) => ({ ...current, nextDate }))}
            />
            <SelectField
              error={fieldError(incomeFields, "confidence")}
              id="income-confidence"
              label="Confidence"
              onChange={(event) => setIncomeForm((current) => ({ ...current, confidence: event.target.value }))}
              options={confidenceOptions}
              value={incomeForm.confidence}
            />
          </div>
          <div className="form-actions">
            <Button disabled={isBusy} type="submit">
              {busyAction === "income" ? "Saving income" : editingIncomeId === null ? "Add income" : "Save income"}
            </Button>
            {editingIncomeId === null ? null : (
              <Button
                disabled={isBusy}
                variant="secondary"
                type="button"
                onClick={resetIncomeForm}
              >
                Cancel edit
              </Button>
            )}
          </div>
        </form>

        <form className="form-panel" id="planned-expenses" onSubmit={(event) => void handleExpenseSubmit(event)}>
          <div className="section-heading-row">
            <div>
              <h2>{editingExpenseId === null ? "Add planned expense" : "Edit planned expense"}</h2>
              <p>Add bills and known costs that should be reserved before the goal deadline.</p>
            </div>
          </div>
          <FormError message={expenseError} />
          <div className="source-fields">
            <SourceFields
              amountDollars={expenseForm.amountDollars}
              fields={expenseFields}
              frequency={expenseForm.frequency}
              name={expenseForm.name}
              nextDate={expenseForm.nextDate}
              prefix="expense"
              onAmountChange={(amountDollars) => setExpenseForm((current) => ({ ...current, amountDollars }))}
              onFrequencyChange={(frequency) => setExpenseForm((current) => ({ ...current, frequency }))}
              onNameChange={(name) => setExpenseForm((current) => ({ ...current, name }))}
              onNextDateChange={(nextDate) => setExpenseForm((current) => ({ ...current, nextDate }))}
            />
            <SelectField
              error={fieldError(expenseFields, "classification")}
              id="expense-classification"
              label="Classification"
              onChange={(event) =>
                setExpenseForm((current) => ({ ...current, classification: event.target.value }))
              }
              options={classificationOptions}
              value={expenseForm.classification}
            />
          </div>
          <div className="form-actions">
            <Button disabled={isBusy} type="submit">
              {busyAction === "expense"
                ? "Saving expense"
                : editingExpenseId === null
                  ? "Add expense"
                  : "Save expense"}
            </Button>
            {editingExpenseId === null ? null : (
              <Button
                disabled={isBusy}
                variant="secondary"
                type="button"
                onClick={resetExpenseForm}
              >
                Cancel edit
              </Button>
            )}
          </div>
        </form>
      </section>

      <section className="input-section-grid">
        <ResourceList
          emptyHelp="Add paychecks, stipends, gifts, or other money you expect before the goal date."
          emptyLabel="No income sources in this plan yet."
          items={inputs.data.incomeSources}
          title="Income in plan"
          onDeactivate={(item) => void handleDeactivateIncome(item.id)}
          onEdit={startIncomeEdit}
          busyAction={busyAction}
          kind="income"
        />
        <ResourceList
          emptyHelp="Add rent, bills, travel, or other known costs due before your target date."
          emptyLabel="No planned expenses in this plan yet."
          items={inputs.data.expenses}
          title="Planned expenses"
          onDeactivate={(item) => void handleDeactivateExpense(item.id)}
          onEdit={startExpenseEdit}
          busyAction={busyAction}
          kind="expense"
        />
      </section>

      <div className="form-actions">
        <ButtonLink to={routes.dashboard}>
          View dashboard
        </ButtonLink>
      </div>
    </section>
  );
}

async function invalidateFinancialPlanningQueries(queryClient: QueryClient) {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboard }),
    queryClient.invalidateQueries({ queryKey: queryKeys.financialInputs }),
    queryClient.invalidateQueries({ queryKey: queryKeys.latestCalculationSnapshot }),
  ]);
}

function RouteHeader() {
  return (
    <PageHeader
      description="Start with cash, then add expected income and planned expenses to plan your weekly safe-to-spend amount."
      title="Financial inputs"
      titleId="financial-inputs-title"
    />
  );
}

function SourceFields({
  amountDollars,
  fields,
  frequency,
  name,
  nextDate,
  onAmountChange,
  onFrequencyChange,
  onNameChange,
  onNextDateChange,
  prefix,
}: {
  amountDollars: string;
  fields: FieldErrors;
  frequency: string;
  name: string;
  nextDate: string;
  onAmountChange: (value: string) => void;
  onFrequencyChange: (value: string) => void;
  onNameChange: (value: string) => void;
  onNextDateChange: (value: string) => void;
  prefix: string;
}) {
  return (
    <>
      <TextField
        error={fieldError(fields, "name")}
        id={`${prefix}-name`}
        label="Name"
        maxLength={120}
        onChange={(event) => onNameChange(event.target.value)}
        required
        type="text"
        value={name}
      />
      <TextField
        error={fieldError(fields, "amount_cents")}
        id={`${prefix}-amount`}
        label="Amount"
        min="0"
        onChange={(event) => onAmountChange(event.target.value)}
        required
        step="0.01"
        type="number"
        value={amountDollars}
      />
      <TextField
        error={fieldError(fields, "next_date")}
        id={`${prefix}-next-date`}
        label="Next date"
        onChange={(event) => onNextDateChange(event.target.value)}
        required
        type="date"
        value={nextDate}
      />
      <SelectField
        error={fieldError(fields, "frequency")}
        id={`${prefix}-frequency`}
        label="Frequency"
        onChange={(event) => onFrequencyChange(event.target.value)}
        options={frequencyOptions}
        value={frequency}
      />
    </>
  );
}

function ResourceList<TItem extends IncomeSourceResponse | PlannedExpenseResponse>({
  busyAction,
  emptyHelp,
  emptyLabel,
  items,
  kind,
  onDeactivate,
  onEdit,
  title,
}: {
  busyAction: string | null;
  emptyHelp: string;
  emptyLabel: string;
  items: TItem[];
  kind: "expense" | "income";
  onDeactivate: (item: TItem) => void;
  onEdit: (item: TItem) => void;
  title: string;
}) {
  return (
    <section className="form-panel resource-panel" aria-labelledby={`${kind}-list-title`}>
      <h2 id={`${kind}-list-title`}>{title}</h2>
      {items.length === 0 ? (
        <div className="resource-empty">
          <strong>{emptyLabel}</strong>
          <p>{emptyHelp}</p>
        </div>
      ) : (
          <div className="resource-list">
            {items.map((item) => (
              <article className="resource-item" key={item.id}>
                <div className="resource-item-main">
                  <div className="resource-item-heading">
                    <h3>{item.name}</h3>
                    <strong>{formatCents(item.amount_cents)}</strong>
                  </div>
                  <p>
                    {frequencyLabel(item.frequency)} · {formatDate(item.next_date)}
                    {kind === "income"
                      ? ` · ${confidenceLabel((item as IncomeSourceResponse).confidence)}`
                      : ` · ${classificationLabel((item as PlannedExpenseResponse).classification)}`}
                  </p>
                </div>
                <div className="resource-actions">
                  <Button disabled={busyAction !== null} variant="secondary" type="button" onClick={() => onEdit(item)}>
                    Edit
                  </Button>
                  <Button
                    variant="secondary"
                    disabled={busyAction !== null}
                    type="button"
                    onClick={() => onDeactivate(item)}
                  >
                    {busyAction === `${kind}-${item.id}` ? "Removing" : "Remove"}
                  </Button>
                </div>
              </article>
            ))}
        </div>
      )}
    </section>
  );
}

function profileToForm(profile: FinancialProfileResponse): ProfileFormState {
  return {
    balanceAsOfDate: profile.balance_as_of_date,
    reserveBufferConfirmed: profile.reserve_buffer_confirmed,
    reserveBufferDollars: centsToDollarInput(profile.reserve_buffer_cents),
    startingCashDollars: centsToDollarInput(profile.starting_cash_cents),
  };
}

function formToProfileRequest(form: ProfileFormState): FinancialProfileRequest {
  return {
    balance_as_of_date: form.balanceAsOfDate,
    reserve_buffer_cents: dollarInputToCents(form.reserveBufferDollars),
    reserve_buffer_confirmed: form.reserveBufferConfirmed,
    starting_cash_cents: dollarInputToCents(form.startingCashDollars),
  };
}

function incomeToForm(income: IncomeSourceResponse): IncomeFormState {
  return {
    amountDollars: centsToDollarInput(income.amount_cents),
    confidence: income.confidence,
    frequency: income.frequency,
    name: income.name,
    nextDate: income.next_date,
  };
}

function formToIncomeRequest(form: IncomeFormState): IncomeSourceRequest {
  return {
    amount_cents: dollarInputToCents(form.amountDollars),
    confidence: form.confidence,
    frequency: form.frequency,
    name: form.name,
    next_date: form.nextDate,
  };
}

function expenseToForm(expense: PlannedExpenseResponse): ExpenseFormState {
  return {
    amountDollars: centsToDollarInput(expense.amount_cents),
    classification: expense.classification,
    frequency: expense.frequency,
    name: expense.name,
    nextDate: expense.next_date,
  };
}

function formToExpenseRequest(form: ExpenseFormState): PlannedExpenseRequest {
  return {
    amount_cents: dollarInputToCents(form.amountDollars),
    classification: form.classification,
    frequency: form.frequency,
    name: form.name,
    next_date: form.nextDate,
  };
}

function handleFormError(
  error: unknown,
  setFields: (fields: FieldErrors) => void,
  setError: (message: string | null) => void,
  fallback: string,
) {
  if (error instanceof ApiError && error.fields !== null) {
    setFields(error.fields);
    setError(firstFormError(error.fields));
    return;
  }
  setError(error instanceof Error ? error.message : fallback);
}
