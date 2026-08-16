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

