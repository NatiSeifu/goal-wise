# User Story: Freelance Retainer With an Uncertain Contract

## Persona

Marcus is a freelance designer. A small monthly retainer is dependable, but a
large client contract is still awaiting signature. Marcus wants the app to make
the risk visible instead of treating a verbal promise as cash in hand.

## Story

As a freelancer with uneven income, Marcus wants to know whether confirmed
income covers his emergency-fund goal after recurring living costs, and what
shortfall remains if the pending contract never arrives.

## Demo context

- Calculation date: August 14, 2026 at 12:00 UTC.
- User time zone: `America/Los_Angeles`.
- Goal: `Freelance runway`.
- Target date: December 31, 2026.

## Inputs

Goal:

- Target amount: `$3,000`.
- Initial saved: `$250`.
- Current saved: `$250`.
- Start date: August 1, 2026.

Financial profile:

- Starting cash outside goal savings: `$600`.
- Balance-as-of date: August 14, 2026.
- Confirmed reserve buffer: `$200`.

Income sources:

| Name | Amount | Next date | Frequency | Confidence |
| --- | ---: | --- | --- | --- |
| Monthly retainer | `$750` | August 21, 2026 | Monthly | Confirmed |
| Pending contract | `$2,500` | September 1, 2026 | One time | Unconfirmed |

Planned expenses:

| Name | Amount | Next date | Frequency | Classification |
| --- | ---: | --- | --- | --- |
| Rent | `$900` | September 1, 2026 | Monthly | Essential |
| Tax set-aside | `$300` | August 31, 2026 | Monthly | Essential |

## Expected `pace-v1` output

| Field | Expected value |
| --- | ---: |
| Confirmed future income | `$3,750` |
| Planned future expenses | `$5,100` |
| Forecast resources | `-$950` |
| Goal gap | `$2,750` |
| Discretionary capacity | `-$3,700` |
| Remaining weeks | `20` |
| Weekly safe-to-spend | `$0` |
| Projected shortfall | `$3,700` |
| Expected savings to date | `$485.19` |
| Pace status | `Off Pace` |

## Demo flow

1. Enter the retainer as confirmed and the contract as unconfirmed.
2. Add rent and tax set-aside as recurring planned expenses.
3. Confirm the reserve buffer and view the conservative dashboard.
4. Show the calculation ledger: the contract is present in the input list but
   absent from official forecast resources.
5. Optionally mark the contract confirmed and save a second calculation to show
   how one explicit assumption changes the result.

## What this proves

- GoalWise is useful when the honest answer is `$0`, not only when a user is on
  track.
- The app separates an entered assumption from an accepted forecast input.
- Shortfall and safe-to-spend are explainable consequences of the same ledger.
- The user can make a deliberate decision without AI inventing certainty.

## Acceptance criteria

- Unconfirmed contract income contributes `$0` to confirmed future income.
- The dashboard reports `Off Pace`, `$0`, and a `$3,700` shortfall.
- Changing confidence creates a new snapshot and visibly identifies the changed
  input category.
- The prior conservative snapshot remains available for comparison.

## MVP boundaries

- No invoice, contract, bank, or tax-provider integration is implied.
- Tax set-aside is a user-entered planned expense, not tax advice.
- AI may explain the committed result but cannot recommend borrowing or promise
  that the contract will arrive.
