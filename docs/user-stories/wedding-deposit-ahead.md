# User Story: Wedding Venue Deposit With Room to Breathe

## Persona

Tara and Dev are planning a small wedding. They have a shared target, stable
paychecks, and a venue deposit due before the final event. They want to know what
they can spend weekly without accidentally consuming money reserved for the
deposit.

## Story

As a couple planning one time-sensitive purchase, Tara wants a single goal view
that includes current savings, future paychecks, rent, and the venue deposit.

## Demo context

- Calculation date: August 14, 2026 at 12:00 UTC.
- User time zone: `America/Los_Angeles`.
- Goal: `Wedding venue deposit`.
- Target date: December 31, 2026.

## Inputs

Goal:

- Target amount: `$5,000`.
- Initial saved: `$1,000`.
- Current saved: `$1,800`.
- Start date: August 1, 2026.

Financial profile:

- Starting cash outside goal savings: `$3,000`.
- Balance-as-of date: August 14, 2026.
- Confirmed reserve buffer: `$500`.

Income sources:

| Name | Amount | Next date | Frequency | Confidence |
| --- | ---: | --- | --- | --- |
| Household salary | `$2,500` | August 28, 2026 | Biweekly | Confirmed |

Planned expenses:

| Name | Amount | Next date | Frequency | Classification |
| --- | ---: | --- | --- | --- |
| Rent | `$1,200` | September 1, 2026 | Monthly | Essential |
| Venue deposit | `$1,500` | October 15, 2026 | One time | Essential |

## Expected `pace-v1` output

| Field | Expected value |
| --- | ---: |
| Confirmed future income | `$22,500` |
| Planned future expenses | `$6,300` |
| Forecast resources | `$18,700` |
| Goal gap | `$3,200` |
| Discretionary capacity | `$15,500` |
| Remaining weeks | `20` |
| Weekly safe-to-spend | `$775` |
| Projected shortfall | `$0` |
| Expected savings to date | `$1,342.10` |
| Pace status | `Ahead` |

## Demo flow

1. Create the wedding goal with `$1,800` currently saved.
2. Add the biweekly salary, recurring rent, and one time venue deposit.
3. Confirm the reserve and open the dashboard.
4. Open calculation details to show how the one time expense is included only
   once and how current savings are compared with expected savings to date.
5. Edit the venue deposit to a higher amount and show a new snapshot without
   mutating the original calculation.

## What this proves

- The happy path still explains every number instead of presenting a black-box
  budget score.
- One time and recurring planning assumptions coexist in one deterministic plan.
- `Ahead` is distinct from `Completed`: the couple has momentum but still has a
  remaining goal gap.
- A meaningful weekly allowance can coexist with a protected future obligation.

## Acceptance criteria

- The venue deposit is counted once before the target date.
- Dashboard status is `Ahead`, with a `$775` weekly safe-to-spend amount.
- Editing the deposit creates a new immutable snapshot and preserves the old
  result for explanation and comparison.
- No frontend formula is needed to reproduce the official values.

## MVP boundaries

- The MVP models the couple's plan as one account owner and one active goal.
- Shared household accounts, split permissions, and multiple simultaneous goals
  are outside this story.
- GoalWise does not provide wedding vendor, credit, or investment advice.
