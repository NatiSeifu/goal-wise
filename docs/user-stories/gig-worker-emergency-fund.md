# User Story: Gig Worker Emergency Fund

## Persona

Sam is a gig worker building a small emergency fund. Some income is reliable
weekly rideshare income, but a monthly side gig is uncertain. Sam needs the app
to be conservative instead of assuming uncertain money will arrive.

## Story

As a gig worker with variable income, Sam wants to know whether confirmed income
alone can support an emergency fund goal after rent, insurance, groceries, and a
reserve buffer.

## Inputs

Calculation context:

- Calculation date: August 14, 2026.
- Time zone: `America/Los_Angeles`.

Goal:

- Name: `Emergency fund`.
- Target amount: `$2,000`.
- Initial saved: `$250`.
- Current saved: `$250`.
- Start date: August 1, 2026.
- Target date: January 31, 2027.

Financial profile:

- Starting cash: `$700`.
- Balance-as-of date: August 14, 2026.
- Reserve buffer: `$300`.
- Reserve buffer confirmed: yes.

Income sources:

| Name | Amount | Next Date | Frequency | Confidence |
| --- | ---: | --- | --- | --- |
| Weekly rideshare payout | `$325` | August 21, 2026 | Weekly | Confirmed |
| Side gig estimate | `$300` | September 1, 2026 | Monthly | Unconfirmed |

Planned expenses:

| Name | Amount | Next Date | Frequency | Classification |
| --- | ---: | --- | --- | --- |
| Rent | `$850` | September 1, 2026 | Monthly | Essential |
| Insurance | `$150` | September 10, 2026 | Monthly | Essential |
| Groceries | `$300` | August 31, 2026 | Monthly | Essential |

## Expected Dashboard Output

Expected `pace-v1` result:

| Field | Value |
| --- | ---: |
| Confirmed future income | `$7,800` |
| Planned future expenses | `$6,800` |
| Forecast resources | `$1,400` |
| Goal gap | `$1,750` |
| Weekly safe-to-spend | `$0` |
| Projected shortfall | `$350` |
| Expected saved by today | `$374` |
| Pace status | `Off Pace` |

## Product Interpretation

Sam's unconfirmed side gig is excluded from forecast resources. Using confirmed
income only, the forecast does not cover the remaining goal gap, so the dashboard
should show `Off Pace`, `$0` weekly safe-to-spend, and a `$350` projected
shortfall.

This story proves GoalWise is intentionally conservative when income is
uncertain. The product should not let unconfirmed income make the safe-to-spend
number look better than the deterministic core can defend.

## MVP Boundaries

- The app does not classify bank transactions in this story.
- The unconfirmed income is visible as an assumption but excluded from the
  official forecast.
- AI must not override the conservative `Off Pace` result.

