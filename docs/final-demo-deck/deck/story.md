# GoalWise Final Demo Story

## Talk Goal

Show that GoalWise is a focused, auditable planning MVP: a user enters one
savings goal and manual assumptions, the backend calculates a weekly
safe-to-spend number deterministically, and the system preserves enough evidence
to explain and defend the result.

## Narrative Arc

1. GoalWise solves one near-term planning question, not broad personal finance.
2. The architecture keeps official money outputs in the backend.
3. The deterministic `pace-v1` engine is isolated from API, database, sessions,
   frontend code, and AI providers.
4. Immutable snapshots make calculations reviewable over time.
5. Auth, CSRF, ownership checks, and Railway configuration constrain the hosted
   demo surface.
6. AI is useful only at the edge: explanations, review, and development support.
7. Verification focuses on calculation correctness, API behavior, ownership,
   migrations, and frontend build safety.
8. The live demo will show the value path, one safe failure case, and engineering
   evidence.

## Timing

Target eight minutes for the slide talk, leaving room inside a ten-minute cap
and preserving the five-minute live demo.
