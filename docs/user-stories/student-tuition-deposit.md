# User Story: Student Tuition Deposit

## Persona

Maya is a college student working part time while preparing for the next term.
She has one near-term goal: save enough for a tuition deposit by the end of the
year. Her income is predictable but not large, and her expenses are mostly fixed.

## Story

As a student with a specific tuition deposit deadline, Maya wants to know how
much she can safely spend each week so she can avoid falling further behind while
still covering rent, groceries, and phone costs.

## Inputs

Calculation context:

- Calculation date: August 14, 2026.
- Time zone: `America/Los_Angeles`.

Goal:

- Name: `Tuition deposit`.
- Target amount: `$1,500`.
- Initial saved: `$300`.
- Current saved: `$300`.
- Start date: August 1, 2026.
- Target date: December 31, 2026.

Financial profile:

- Starting cash: `$2,200`.
- Balance-as-of date: August 14, 2026.
- Reserve buffer: `$200`.
- Reserve buffer confirmed: yes.

Income sources:

| Name | Amount | Next Date | Frequency | Confidence |
| --- | ---: | --- | --- | --- |
| Part-time work | `$900` | August 28, 2026 | Biweekly | Confirmed |

Planned expenses:

| Name | Amount | Next Date | Frequency | Classification |
| --- | ---: | --- | --- | --- |
| Rent | `$700` | September 1, 2026 | Monthly | Essential |
| Groceries | `$250` | August 31, 2026 | Monthly | Essential |
| Phone | `$80` | September 5, 2026 | Monthly | Essential |

## Expected Dashboard Output

Expected `pace-v1` result:

| Field | Value |
| --- | ---: |
| Confirmed future income | `$8,100` |
| Planned future expenses | `$4,370` |
| Forecast resources | `$5,730` |
| Goal gap | `$1,200` |
| Weekly safe-to-spend | `$226` |
| Projected shortfall | `$0` |
| Expected saved by today | `$402` |
| Pace status | `At Risk` |

## Product Interpretation

Maya has enough forecast resources to cover the goal gap, so the projected
shortfall is `$0`. She is still `At Risk` because her current saved amount is
behind the expected savings curve for August 14.

This story proves that `At Risk` does not necessarily mean the goal is impossible.
It means the user is behind today and should be cautious with weekly spending.

## MVP Boundaries

- The dashboard should not recommend AI-generated coaching.
- The frontend should not calculate the safe-to-spend amount.
- Transaction import and category budgeting are not part of this story.

