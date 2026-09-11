# GoalWise Final Demo Story

## Talk Goal

Show a real user path through GoalWise: registration, guided setup, one savings
goal, a backend-owned weekly result, a rejected planning import, and an
explanation tied to the committed calculation. The technical argument is that
the result remains reproducible, reviewable, and isolated from runtime AI.

## Narrative Arc

1. The product begins with one planning question: can this user reach the goal,
   and what can they spend this week?
2. The first run is explicit: register, follow setup, create a goal, enter
   assumptions, and read the dashboard.
3. Official money outputs stay in the backend and come from `pace-v1`.
4. Immutable snapshots preserve what was calculated and why.
5. Sessions, CSRF, and ownership checks protect the hosted workflow.
6. CSV import is previewed before commit; malformed input is a useful visible
   failure case.
7. AI explains a committed result; it does not calculate or override it.
8. GitHub CI, Railway deployment, and boundary-focused tests provide the
   engineering evidence.

## Timing

Target eight minutes for the slide talk, leaving room inside a ten-minute cap
and preserving the five-minute live demo.
