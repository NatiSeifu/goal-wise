# GoalWise User Stories

These stories describe realistic MVP users and the dashboard behavior their data
should produce under `pace-v1`.

Shared assumptions:

- Calculation date: August 14, 2026.
- User time zone: `America/Los_Angeles`.
- Money values are entered by users as dollars and persisted by the backend as
  integer cents.
- Dashboard outputs come from the deterministic backend pace engine, not from
  frontend calculations or AI.

## Stories

| Story | Dashboard State | What It Proves |
| --- | --- | --- |
| [Student tuition deposit](student-tuition-deposit.md) | `At Risk` | A user can have no projected shortfall but still be behind the expected savings curve. |
| [Young professional moving fund](young-professional-moving-fund.md) | `On Track` | A user with strong confirmed resources and adequate current savings gets a usable weekly safe-to-spend amount. |
| [Gig worker emergency fund](gig-worker-emergency-fund.md) | `Off Pace` | Unconfirmed income is excluded, producing a conservative result when confirmed resources do not cover the goal gap. |
| [Healthcare deductible](healthcare-deductible.md) | `On Track` | A high-consequence deadline, reserve buffer, and unconfirmed bonus remain visible in one explainable plan. |
| [Freelance retainer gap](freelance-retainer-gap.md) | `Off Pace` | A conservative `$0` allowance and explicit shortfall make uncertain contract income actionable. |
| [Wedding venue deposit](wedding-deposit-ahead.md) | `Ahead` | Recurring income and a one-time obligation produce a protected goal with room to spend. |
| [Completed emergency goal](completed-emergency-goal.md) | `Completed` | A zero goal gap is a real lifecycle outcome and remains auditable before archival. |

## Production demo workflows

| Workflow | What it proves |
| --- | --- |
| [Recoverable planning import and explainable review](demo-workflow-runbook.md) | Canonical CSV preview, explicit replacement, atomic confirmation, immutable snapshots, and bounded explain-only AI behavior. |

These are demo-ready narratives, not promises of capabilities outside the MVP.
Every monetary expectation is an example of the deterministic backend contract;
the UI should render the returned values rather than reimplement the formulas.

## Local demo accounts

Run `make seed-user-stories` after `make backend-stack-rebuild` and before
`make dev-up`'s frontend is opened. The script creates the accounts below plus
the original three stories, then prints each user's calculated status and
allowance. It is guarded to accept only localhost API URLs.

All seeded accounts use the local-only password
`CorrectHorseBatteryStaple123!`.

| Account | Story state | Use it to demonstrate |
| --- | --- | --- |
| `elena.deductible@example.com` | `On Track` | Unconfirmed bonus, reserve buffer, and a high-consequence one-time expense. |
| `marcus.freelance@example.com` | `Off Pace` | Conservative treatment of uncertain contract income and explicit shortfall. |
| `tara.wedding@example.com` | `Ahead` | Recurring income plus a protected one-time venue deposit. |
| `noah.completed@example.com` | `Completion transition` | Start with a ready near-complete plan, then edit to the target and show completion/archive lifecycle. |
