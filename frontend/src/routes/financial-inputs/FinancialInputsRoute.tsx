import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { ApiError, type FieldErrors } from "../../api/errors.ts";
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
import { FormError } from "../../components/feedback/FormError.tsx";
import { RouteLoading } from "../../components/feedback/RouteLoading.tsx";
import { SelectField } from "../../components/ui/SelectField.tsx";
import { TextField } from "../../components/ui/TextField.tsx";
import { useFinancialInputs } from "../../features/financial-inputs/useFinancialInputs.ts";
import { centsToDollarInput, dollarInputToCents, formatCents, formatDate } from "../../utils/format.ts";
import { fieldError, firstFormError } from "../../utils/forms.ts";

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
  { label: "One time", value: "one_time" },
  { label: "Weekly", value: "weekly" },
  { label: "Biweekly", value: "biweekly" },
  { label: "Monthly", value: "monthly" },
];

const confidenceOptions = [
  { label: "Confirmed", value: "confirmed" },
  { label: "Unconfirmed", value: "unconfirmed" },
];

const classificationOptions = [
  { label: "Essential", value: "essential" },
  { label: "Discretionary", value: "discretionary" },
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
  const inputs = useFinancialInputs();
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

  useEffect(() => {
    if (inputs.status === "ready" && inputs.data.profile !== null) {
      setProfileForm(profileToForm(inputs.data.profile));
    }
  }, [inputs.data, inputs.status]);

  if (inputs.status === "loading") {
    return <RouteLoading fullPage={false} label="Loading financial inputs" />;
  }

  if (inputs.status === "error") {
    return (
      <section className="form-page" aria-labelledby="financial-inputs-title">
        <RouteHeader />
        <div className="state-panel error">
          <h2>Financial inputs unavailable</h2>
          <p>{inputs.error}</p>
        </div>
      </section>
    );
  }

  async function reloadAfterSuccess(message: string) {
    setSuccessMessage(message);
    await inputs.reload();
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
      await reloadAfterSuccess("Financial profile saved. The backend recalculated when inputs were ready.");
    } catch (error) {
      handleFormError(error, setProfileFields, setProfileError, "Financial profile could not be saved.");
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
      setIncomeForm(emptyIncomeForm);
      setEditingIncomeId(null);
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
      setExpenseForm(emptyExpenseForm);
      setEditingExpenseId(null);
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
      await reloadAfterSuccess("Income source deactivated.");
    } catch (error) {
      setIncomeError(error instanceof Error ? error.message : "Income source could not be deactivated.");
    } finally {
      setBusyAction(null);
    }
  }

  async function handleDeactivateExpense(expenseId: string) {
    setBusyAction(`expense-${expenseId}`);
    setSuccessMessage(null);
    try {
      await deletePlannedExpense(expenseId);
      await reloadAfterSuccess("Planned expense deactivated.");
    } catch (error) {
      setExpenseError(error instanceof Error ? error.message : "Planned expense could not be deactivated.");
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <section className="form-page wide" aria-labelledby="financial-inputs-title">
      <RouteHeader />
      {successMessage === null ? null : (
        <p className="form-success" role="status">
          {successMessage}
        </p>
      )}

      <form className="form-panel" onSubmit={(event) => void handleProfileSubmit(event)}>
        <h2>Financial profile</h2>
        <FormError message={profileError} />
        <div className="form-grid">
          <TextField
            error={fieldError(profileFields, "starting_cash_cents")}
            id="profile-starting-cash"
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
          <label className="checkbox-field" htmlFor="profile-reserve-confirmed">
            <input
              checked={profileForm.reserveBufferConfirmed}
              id="profile-reserve-confirmed"
              onChange={(event) =>
                setProfileForm((current) => ({ ...current, reserveBufferConfirmed: event.target.checked }))
              }
              type="checkbox"
            />
            <span>Reserve buffer confirmed</span>
          </label>
        </div>
        <div className="form-actions">
          <button className="button primary" disabled={busyAction === "profile"} type="submit">
            {busyAction === "profile" ? "Saving profile" : "Save profile"}
          </button>
        </div>
      </form>

      <section className="input-section-grid">
        <form className="form-panel" onSubmit={(event) => void handleIncomeSubmit(event)}>
          <h2>{editingIncomeId === null ? "Add income source" : "Edit income source"}</h2>
          <FormError message={incomeError} />
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
          <div className="form-actions">
            <button className="button primary" disabled={busyAction === "income"} type="submit">
              {busyAction === "income" ? "Saving income" : editingIncomeId === null ? "Add income" : "Save income"}
            </button>
            {editingIncomeId === null ? null : (
              <button
                className="button secondary"
                type="button"
                onClick={() => {
                  setEditingIncomeId(null);
                  setIncomeForm(emptyIncomeForm);
                }}
              >
                Cancel edit
              </button>
            )}
          </div>
        </form>

        <form className="form-panel" onSubmit={(event) => void handleExpenseSubmit(event)}>
          <h2>{editingExpenseId === null ? "Add planned expense" : "Edit planned expense"}</h2>
          <FormError message={expenseError} />
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
          <div className="form-actions">
            <button className="button primary" disabled={busyAction === "expense"} type="submit">
              {busyAction === "expense"
                ? "Saving expense"
                : editingExpenseId === null
                  ? "Add expense"
                  : "Save expense"}
            </button>
            {editingExpenseId === null ? null : (
              <button
                className="button secondary"
                type="button"
                onClick={() => {
                  setEditingExpenseId(null);
                  setExpenseForm(emptyExpenseForm);
                }}
              >
                Cancel edit
              </button>
            )}
          </div>
        </form>
      </section>

      <section className="input-section-grid">
        <ResourceList
          emptyLabel="No active income sources yet."
          items={inputs.data.incomeSources}
          title="Active income"
          onDeactivate={(item) => void handleDeactivateIncome(item.id)}
          onEdit={(item) => {
            setEditingIncomeId(item.id);
            setIncomeForm(incomeToForm(item));
          }}
          busyAction={busyAction}
          kind="income"
        />
        <ResourceList
          emptyLabel="No active planned expenses yet."
          items={inputs.data.expenses}
          title="Planned expenses"
          onDeactivate={(item) => void handleDeactivateExpense(item.id)}
          onEdit={(item) => {
            setEditingExpenseId(item.id);
            setExpenseForm(expenseToForm(item));
          }}
          busyAction={busyAction}
          kind="expense"
        />
      </section>

      <div className="form-actions">
        <Link className="button secondary" to={routes.dashboard}>
          View dashboard
        </Link>
      </div>
    </section>
  );
}

function RouteHeader() {
  return (
    <header className="dashboard-header">
      <div>
        <h1 id="financial-inputs-title">Financial inputs</h1>
        <p>Manual assumptions used by the backend pace engine for this MVP.</p>
      </div>
    </header>
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
  emptyLabel,
  items,
  kind,
  onDeactivate,
  onEdit,
  title,
}: {
  busyAction: string | null;
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
        <p className="panel-copy">{emptyLabel}</p>
      ) : (
        <div className="resource-list">
          {items.map((item) => (
            <article className="resource-item" key={item.id}>
              <div>
                <h3>{item.name}</h3>
                <p>
                  {formatCents(item.amount_cents)} · {item.frequency} · {formatDate(item.next_date)}
                </p>
              </div>
              <div className="resource-actions">
                <button className="button secondary" type="button" onClick={() => onEdit(item)}>
                  Edit
                </button>
                <button
                  className="button secondary"
                  disabled={busyAction === `${kind}-${item.id}`}
                  type="button"
                  onClick={() => onDeactivate(item)}
                >
                  {busyAction === `${kind}-${item.id}` ? "Removing" : "Deactivate"}
                </button>
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
