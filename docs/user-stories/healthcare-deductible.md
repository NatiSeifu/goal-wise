# User Story: Healthcare Deductible Before Open Enrollment

## Persona

Elena is a full-time employee whose partner is changing jobs. Before the new
insurance plan starts, Elena wants to reserve money for a likely medical
deductible. Her employer paycheck is reliable, but a discretionary annual bonus
is not guaranteed.

## Story

As a household planner facing a fixed medical deadline, Elena wants a weekly
spending number that protects the deductible and reserve while showing whether
her current savings are keeping pace.

## Demo context

- Calculation date: August 14, 2026 at 12:00 UTC.
- User time zone: `America/Los_Angeles`.
- Goal: `Medical deductible`.
- Target date: December 31, 2026.

## Inputs

Goal:

- Target amount: `$1,800`.
- Initial saved: `$400`.
- Current saved: `$500`.
- Start date: August 1, 2026.

Financial profile:

- Starting cash outside goal savings: `$1,200`.
- Balance-as-of date: August 14, 2026.
- Confirmed reserve buffer: `$300`.

Income sources:

| Name | Amount | Next date | Frequency | Confidence |
| --- | ---: | --- | --- | --- |
| Employer paycheck | `$1,800` | August 28, 2026 | Biweekly | Confirmed |
| Annual bonus | `$1,000` | October 1, 2026 | One time | Unconfirmed |

Planned expenses:

| Name | Amount | Next date | Frequency | Classification |
| --- | ---: | --- | --- | --- |
| Rent | `$900` | September 1, 2026 | Monthly | Essential |
| Deductible payment | `$600` | October 15, 2026 | One time | Essential |

## Expected `pace-v1` output

| Field | Expected value |
| --- | ---: |
| Confirmed future income | `$16,200` |
| Planned future expenses | `$4,200` |
| Forecast resources | `$12,900` |
| Goal gap | `$1,300` |
| Discretionary capacity | `$11,600` |
| Remaining weeks | `20` |
| Weekly safe-to-spend | `$580` |
| Projected shortfall | `$0` |
| Expected savings to date | `$519.73` |
| Pace status | `On Track` |

## Demo flow

1. Create Elena's goal and enter the current saved amount separately from
   starting cash.
2. Add the paycheck as confirmed and the bonus as unconfirmed.
3. Add rent and the deductible payment as planned expenses.
4. Confirm a `$300` reserve buffer.
5. Show the dashboard and calculation details.
6. Change the bonus to confirmed, save, and show the new immutable snapshot and
   changed-input explanation. The official result remains backend-owned.

## What this proves

- GoalWise handles a common high-consequence expense without requiring bank
  synchronization.
- Unconfirmed income does not inflate the official spending allowance.
- Goal savings and general cash remain separate inputs.
- A user can have a healthy forecast and still see the exact assumptions behind
  the result.

## Acceptance criteria

- The bonus is visible as unconfirmed and excluded from confirmed future income.
- The deductible is included in planned expenses through its date.
- The dashboard shows the values above without frontend-derived arithmetic.
- Saving the changed bonus creates a new snapshot; the prior snapshot remains
  unchanged.
- Any AI explanation describes the snapshot but cannot change `$580` or
  `On Track`.

## MVP boundaries

- No insurance-account integration or medical advice is implied.
- Elena manually enters the bonus confidence and planned expenses.
- GoalWise does not determine whether the deductible amount is medically or
  financially sufficient; it reports the entered plan.
