# User Story: Young Professional Moving Fund

## Persona

Jordan is an early-career professional planning a move for a new apartment. He
has a stable paycheck, known monthly obligations, and a one-time moving supply
expense. He wants a simple weekly number that lets him keep spending without
putting the move at risk.

## Story

As a young professional saving for moving costs, Jordan wants to confirm that his
current savings and upcoming paychecks keep him on track while accounting for
rent, car payments, utilities, and moving supplies.

## Inputs

Calculation context:

- Calculation date: August 14, 2026.
- Time zone: `America/Los_Angeles`.

Goal:

- Name: `Moving fund`.
- Target amount: `$3,000`.
- Initial saved: `$900`.
- Current saved: `$1,125`.
- Start date: August 1, 2026.
- Target date: November 15, 2026.

Financial profile:

- Starting cash: `$3,800`.
- Balance-as-of date: August 14, 2026.
- Reserve buffer: `$500`.
- Reserve buffer confirmed: yes.

Income sources:

| Name | Amount | Next Date | Frequency | Confidence |
| --- | ---: | --- | --- | --- |
| Salary | `$2,200` | August 28, 2026 | Biweekly | Confirmed |

Planned expenses:

| Name | Amount | Next Date | Frequency | Classification |
| --- | ---: | --- | --- | --- |
| Rent | `$1,450` | September 1, 2026 | Monthly | Essential |
| Car payment | `$350` | September 10, 2026 | Monthly | Essential |
| Utilities | `$250` | September 5, 2026 | Monthly | Essential |
| Moving supplies | `$600` | October 15, 2026 | One time | Essential |

## Expected Dashboard Output

Expected `pace-v1` result:

| Field | Value |
| --- | ---: |
| Confirmed future income | `$13,200` |
| Planned future expenses | `$6,750` |
| Forecast resources | `$9,750` |
| Goal gap | `$1,875` |
| Weekly safe-to-spend | `$562` |
| Projected shortfall | `$0` |
| Expected saved by today | `$1,157` |
| Pace status | `On Track` |

## Product Interpretation

Jordan is close enough to the expected savings curve and has enough confirmed
resources to cover the remaining goal gap. The dashboard should present this as
`On Track` with a meaningful weekly safe-to-spend amount.

This story proves the happy path: a user can enter realistic obligations and get
a clear, backend-owned spending allowance.

## MVP Boundaries

- The app supports one active goal, not multiple moving-related subgoals.
- The one-time moving supply expense is represented as a planned expense, not a
  transaction import.
- The dashboard result is deterministic and does not use AI.

