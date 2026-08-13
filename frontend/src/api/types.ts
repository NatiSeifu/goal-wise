export type IsoDate = string;
export type IsoDateTime = string;

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

export type UserResponse = {
  id: string;
  email: string;
  time_zone: string;
};

export type AuthPayload = {
  user: UserResponse;
  csrf_token: string;
};

export type AuthResponse = {
  item: AuthPayload;
};

export type RegisterRequest = {
  email: string;
  password: string;
  time_zone: string;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type GoalRequest = {
  name: string;
  target_cents: number;
  initial_saved_cents: number;
  current_saved_cents: number;
  start_date: IsoDate;
  target_date: IsoDate;
};

export type GoalResponse = {
  id: string;
  name: string;
  target_cents: number;
  initial_saved_cents: number;
  current_saved_cents: number;
  start_date: IsoDate;
  target_date: IsoDate;
  status: string;
  archived_at: IsoDateTime | null;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
};

export type GoalItemResponse = {
  item: GoalResponse | null;
};

export type FinancialProfileRequest = {
  starting_cash_cents: number;
  balance_as_of_date: IsoDate;
  reserve_buffer_cents: number;
  reserve_buffer_confirmed: boolean;
};

export type FinancialProfileResponse = {
  id: string;
  starting_cash_cents: number;
  balance_as_of_date: IsoDate;
  reserve_buffer_cents: number;
  reserve_buffer_confirmed: boolean;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
};

export type FinancialProfileItemResponse = {
  item: FinancialProfileResponse | null;
};

export type IncomeSourceRequest = {
  name: string;
  amount_cents: number;
  next_date: IsoDate;
  frequency: string;
  confidence: string;
};

export type IncomeSourceResponse = {
  id: string;
  name: string;
  amount_cents: number;
  next_date: IsoDate;
  frequency: string;
  confidence: string;
  active: boolean;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
};

export type IncomeSourceItemResponse = {
  item: IncomeSourceResponse;
};

export type IncomeSourceListResponse = {
  items: IncomeSourceResponse[];
};

export type PlannedExpenseRequest = {
  name: string;
  amount_cents: number;
  next_date: IsoDate;
  frequency: string;
  classification: string;
};

export type PlannedExpenseResponse = {
  id: string;
  name: string;
  amount_cents: number;
  next_date: IsoDate;
  frequency: string;
  classification: string;
  active: boolean;
  created_at: IsoDateTime;
  updated_at: IsoDateTime;
};

export type PlannedExpenseItemResponse = {
  item: PlannedExpenseResponse;
};

export type PlannedExpenseListResponse = {
  items: PlannedExpenseResponse[];
};

export type DashboardGoalSummary = {
  id: string;
  name: string;
  target_cents: number;
  current_saved_cents: number;
  target_date: IsoDate;
};

export type DashboardPaceSummary = {
  pace_status: string;
  weekly_safe_to_spend_cents: number;
  projected_shortfall_cents: number;
  remaining_weeks: number;
  progress_percentage: number;
  current_week_opening_allowance_cents: number;
  current_week_remainder_cents: number;
};

export type DashboardItem = {
  status: string;
  missing_inputs: string[];
  snapshot_id: string | null;
  calculated_at: IsoDateTime | null;
  formula_version: string | null;
  goal: DashboardGoalSummary | null;
  pace: DashboardPaceSummary | null;
  explanation: Record<string, JsonValue> | null;
  changed_from_previous: Record<string, JsonValue> | null;
};

export type DashboardResponse = {
  item: DashboardItem;
};

export type CalculationSnapshotResponse = {
  id: string;
  user_id: string;
  goal_id: string;
  formula_version: string;
  trigger: string;
  normalized_input_json: Record<string, JsonValue>;
  result_json: Record<string, JsonValue>;
  calculated_at: IsoDateTime;
  created_at: IsoDateTime;
};

export type CalculationSnapshotItemResponse = {
  item: CalculationSnapshotResponse | null;
};
