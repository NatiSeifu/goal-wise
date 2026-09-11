# User Story: Completed Emergency Goal

## Persona

Noah set a small emergency goal after replacing a failed laptop. He has now set
aside the full target amount and wants the product to acknowledge completion
without silently turning the old goal into a new one.

## Story

As a user who has reached a savings target, Noah wants a clear completed state
and an auditable calculation that shows a zero goal gap.

## Demo context

- Calculation date: August 14, 2026 at 12:00 UTC.
- User time zone: `America/Los_Angeles`.
- Goal: `Laptop replacement fund`.
- Target date: December 31, 2026.

## Inputs

- Target amount: `$1,200`.
- Initial saved: `$0`.
- Current saved: `$1,200`.
- Start date: August 1, 2026.
- Starting cash outside goal savings: `$500`.
- Balance-as-of date: August 14, 2026.
- Reserve buffer: `$100`.
- No future income or planned expenses.

## Expected `pace-v1` output

| Field | Expected value |
| --- | ---: |
| Confirmed future income | `$0` |
| Planned future expenses | `$0` |
| Forecast resources | `$400` |
| Goal gap | `$0` |
| Discretionary capacity | `$400` |
| Remaining weeks | `20` |
| Weekly safe-to-spend | `$20` |
| Projected shortfall | `$0` |
| Expected savings to date | `$102.63` |
| Pace status | `Completed` |

## Demo flow

1. Create the goal with `$1,200` as current saved.
2. Save the goal and open the dashboard.
3. Show that `Completed` is evaluated before other pace states because the goal
   gap is zero.
4. Open the goal lifecycle control and archive the goal only as an explicit user
   action.

## What this proves

- Completion is a real lifecycle outcome, not merely a green progress color.
- A completed goal does not require future income to be considered complete.
- The app keeps the completed calculation auditable before archival.

## Acceptance criteria

- Goal gap and projected shortfall are both `$0`.
- Pace status is `Completed`.
- The dashboard does not show an `Off Pace` or `At Risk` warning.
- Archiving is explicit and does not mutate the immutable snapshot.

## MVP boundaries

- Completing this goal does not create a second active goal automatically.
- Multi-goal history and goal recommendation behavior are deferred.
