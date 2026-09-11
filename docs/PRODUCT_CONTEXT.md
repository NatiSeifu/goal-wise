# GoalWise Product Context

This document is the compact product truth source for agents working on UI mockups, screenshots, frontend surfaces, and SRS visuals.

Use it with the SRS, ADRs, specs, `ARCHITECTURE.md`, and `DESIGN.md`. If this document conflicts with a numbered spec or ADR, stop and warn the user before changing product behavior.

## Product Summary

GoalWise is a goal-oriented budgeting app for understanding whether a user is on pace to reach one savings goal.

The MVP turns a goal, current cash, expected income, planned expenses, and a reserve buffer into backend-owned planning outputs:

- weekly safe-to-spend amount;
- pace status;
- projected shortfall;
- calculation details;
- immutable calculation snapshots.

GoalWise is not a general-purpose budget app in the current MVP. It is a focused planning loop around one active savings goal.

## Current MVP Capabilities

The current MVP supports or is being built toward:

- account registration, login, logout, sessions, and CSRF protection;
- user-owned data isolation;
- one active savings goal;
- manual financial profile setup;
- manual income sources;
- manual planned expenses;
- deterministic `pace-v1` calculations;
- immutable calculation snapshots;
- dashboard-ready values returned by the backend;
- canonical planning CSV import with preview and explicit confirmation.
- optional runtime AI explanations of committed snapshots.

## Deferred Capabilities

Do not present these as working MVP behavior unless the user explicitly asks and the scope docs are updated:

- multiple active goals;
- raw bank-statement or transaction import;
- transaction correction and duplicate handling;
- AI transaction classification;
- AI-generated financial decisions;
- export/delete account workflows;
- background scheduling;
- bank sync or live financial account connections;
- native mobile apps;
- gamification such as levels, XP, streaks, or badges.

Deferred features may appear only as clearly marked future-state concepts, not as implemented or promised current behavior.

The current planning CSV increment is specified in
[SPEC-0010](specs/0010-planning-csv-import.md). It accepts one complete,
already-structured GoalWise plan, previews the normalized values, and replaces
the active setup only after explicit confirmation. Raw bank-statement or
transaction import remains future-state.

## Real Product Entities

Use these entities when designing UI or mockups:

- **User**: authenticated account owner.
- **Goal**: one active savings target with target amount, initial saved amount, current saved amount, start date, target date, and lifecycle status. Current saved amount is money already set aside toward this goal.
- **Financial profile**: starting cash outside current goal savings, balance-as-of date, and reserve buffer.
- **Income source**: manual expected income with amount, date recurrence, confidence, and active state.
- **Planned expense**: manual expected expense with amount, date recurrence, classification, and active state.
- **Calculation snapshot**: immutable record of normalized inputs and deterministic result.
- **Weekly plan**: backend-created plan for current weekly allowance.

Transactions are part of the broader SRS but deferred from the current MVP implementation.

## AI Boundary

AI may support design-time work such as drafting ADRs, diagrams, tests, review checklists, and UI variants.

At runtime, the optional AI explanation layer may explain a committed snapshot,
but it must not calculate or override:

- safe-to-spend;
- pace status;
- projected shortfall;
- snapshot contents;
- official dashboard metrics.

AI is unavailable without blocking the deterministic planning workflow. Provider
requests are server-side, minimized, schema-validated, and scoped to the
authenticated user's latest committed snapshot.

The deterministic backend pace engine is the source of truth for financial outputs.

## UI Truth Rules

When creating UI mockups or frontend screens:

- Do not invent metrics, entities, filters, actions, navigation, or calculations that are not represented in this document, the SRS scope mapping, specs, or backend API contracts.
- If a requested UI needs unsupported backend behavior, flag the gap instead of faking it.
- The frontend may format and visualize backend values, but it must not duplicate official pace-engine formulas.
- Avoid showing raw transaction descriptions in durable snapshots or SRS visuals for MVP behavior.
- Screenshots for SRS or slides should come from actual rendered UI, not standalone generated images, when the goal is to show app screens.

## Visual Direction From Reference Mockup

The rough dashboard reference provided by the user may guide:

- left-sidebar app shell;
- clean personal-finance dashboard tone;
- calm green/blue trust palette;
- goal-first information hierarchy;
- summary metrics above detailed content;
- progress bars, status treatments, and clear row/card scanability;
- top-right primary action area;
- simple filter/sort affordance patterns when supported by scope.

The reference mockup must not override product scope. Do not copy unsupported behaviors such as multiple active goals, transactions pages, analytics pages, AI insights, accounts management, XP levels, or rebalancing actions unless they are explicitly marked as future-state and approved for the artifact being produced.

## Screenshot Artifacts

Rendered UI screenshots intended for SRS, slides, or review materials should be deterministic:

- use fixed viewport sizes;
- use committed mock data derived from real entities;
- avoid invented backend capabilities;
- store intentional final assets under `docs/assets/mockups/` or a more specific docs asset directory;
- keep transient export output out of version control unless the user asks to preserve it.
