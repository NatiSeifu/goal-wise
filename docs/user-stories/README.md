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
