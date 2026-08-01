# SPEC-0005: Date and Time Semantics

Status: Accepted
Last Updated: 2026-08-01
Related ADRs: ADR-0002, ADR-0003, ADR-0004
Related Specs: SPEC-0003, SPEC-0004
Source Requirements: SRS Section 3.3, FR-GOAL-002, FR-FIN-005, FR-PACE-003, FR-PACE-007, FR-PACE-008, FR-PACE-009, NFR-ACC-002

## Purpose

Define how GoalWise handles UTC timestamps, user-local date-only values, recurrence expansion, same-day occurrences, remaining weeks, and weekly plan boundaries.

## Core Rules

- Store timestamps in UTC.
- Store user-facing financial dates as date-only values.
- Each user has an IANA time zone.
- Use the user's IANA time zone for current local date, date validation, recurrence expansion, remaining weeks, weekly plan boundaries, and date presentation.
- Do not collect times for income sources or planned expenses in the MVP.

## Date and Timestamp Types

Use UTC timestamps for:

- `created_at`
- `updated_at`
- `archived_at`
- `calculated_at`
- session timestamps
- audit timestamps

Use date-only local calendar values for:

- goal `start_date`
- goal `target_date`
- financial profile `balance_as_of_date`
- income source `next_date`
- planned expense `next_date`
- transaction `date`
- weekly plan `week_start`

## Current Local Date

For a calculation timestamp:

```text
calculation_local_date =
  date part of calculation_timestamp_utc converted to user_time_zone
```

Use `calculation_local_date` for target-date validation, recurrence filtering, expected savings to date, and remaining weeks.

## Goal Date Validation

When creating or updating an active goal:

```text
target_date > current local date
```

The current local date is evaluated in the user's configured IANA time zone.

## Financial Profile Date Validation

When creating or updating a financial profile:

```text
balance_as_of_date <= current local date
```

The current local date is evaluated in the user's configured IANA time zone.

## Income and Expense Occurrence Filtering

Income sources and planned expenses are date-only local calendar events.

Include occurrences in future forecasts only when:

```text
occurrence_date > calculation_local_date
and
occurrence_date <= target_date
```

Exclude same-day income and planned-expense occurrences from future forecasts because the MVP does not collect occurrence times.

Rationale:

- The SRS says occurrences are after the calculation timestamp.
- The MVP stores occurrence dates, not occurrence times.
- Including same-day date-only events until local end-of-day could overcount events that already happened.
- Excluding same-day date-only events is conservative and deterministic.

## Recurrence Expansion

Allowed MVP frequencies:

- `one_time`
- `weekly`
- `biweekly`
- `monthly`

Expansion rules:

- Start from `next_date`.
- Generate occurrences in the user's local calendar.
- Stop after `target_date`.
- Apply filtering after expansion.
- Monthly recurrence uses the same day-of-month when possible.
- If a later month does not have the same day-of-month, use that month's final calendar day.

Example:

```text
next_date = 2026-01-31
frequency = monthly
occurrences = 2026-01-31, 2026-02-28, 2026-03-31, ...
```

## Remaining Weeks

Calculate remaining weeks from the user's local calculation date:

```text
days_remaining = target_date - calculation_local_date
remaining_weeks = max(1, ceiling(days_remaining / 7))
```

If the target date is fewer than seven days away, `remaining_weeks = 1`.

If `calculation_local_date = target_date`, `remaining_weeks = 1`.

Active goal creation and update validation prevents target dates earlier than or equal to the current local date, but calculation code should still guard against edge cases.

## Weekly Plan Boundaries

Weekly plans use Monday-through-Sunday local weeks.

```text
week_start = local date for Monday of the user's current local week
```

At Monday 00:00 in the user's time zone, GoalWise creates the current weekly plan using the latest weekly safe-to-spend value as the opening allowance.

MVP behavior may create the current weekly plan lazily on authenticated dashboard access when:

- a valid latest calculation snapshot exists;
- no weekly plan exists for the current local `week_start`.

Midweek recalculation must not replace the current week's opening allowance. The recalculated amount is used for the next weekly plan.

## Transactions

Transaction support is post-MVP unless explicitly pulled into scope.

When implemented:

- Transaction dates are date-only local calendar values.
- Transactions dated on or before `balance_as_of_date` are excluded from current cash to prevent double counting.
- Accepted discretionary outflows dated within the current local Monday-through-Sunday week reduce current-week remainder.

## Verification

Required tests:

- UTC calculation timestamp converts to the correct user local date.
- Target date must be later than the user's current local date.
- Balance-as-of date cannot be later than the user's current local date.
- Same-day income and planned-expense occurrences are excluded from future forecasts.
- Tomorrow's income and planned-expense occurrences are included when on or before target date.
- Occurrences after target date are excluded.
- Less-than-seven-days target uses one remaining week.
- Calculation local date equal to target date uses one remaining week.
- Weekly plan `week_start` is Monday in the user's local time zone.
- Midweek recalculation does not replace the current week's opening allowance.

