# SPEC-0009: UI Mockup and Screenshot Workflow

Status: Accepted
Last Updated: 2026-08-08
Related ADRs: ADR-0002, ADR-0007, ADR-0008
Related Specs: SPEC-0007, SPEC-0008

## Purpose

Define a repo-grounded workflow for creating GoalWise UI mockups and screenshot assets for SRS, slides, design reviews, and future frontend implementation.

The goal is to avoid disconnected AI-generated UI images. UI artifacts should be derived from the product context, SRS, ADRs, specs, backend data contracts, and actual rendered UI code.

## Source of Truth Order

Agents and contributors must use this order when UI artifacts disagree:

1. SRS scope mapping in `docs/specs/0007-srs-traceability-and-mvp-scope.md`.
2. Accepted ADRs in `docs/adr/`.
3. Accepted implementation specs in `docs/specs/`.
4. Backend API schemas, models, and service behavior.
5. `DESIGN.md` and `ARCHITECTURE.md`.
6. `docs/PRODUCT_CONTEXT.md`.
7. Visual reference mockups supplied by the user.

Visual references guide presentation and layout only. They do not define product capabilities.

## Required Agent Workflow

Before creating or changing UI mockups, an agent must:

1. Read `docs/PRODUCT_CONTEXT.md`.
2. Read the SRS MVP scope mapping in `SPEC-0007`.
3. Read the relevant ADRs and specs for the feature being shown.
4. Inspect available backend schemas or API contracts for fields and actions.
5. Produce or update a UI data contract that lists the entities, fields, actions, empty states, and deferred capabilities used by the mockup.
6. Warn the user if the requested UI needs unsupported product behavior.

The UI data contract may be a section in the mockup README, a route-level mockup brief, or a dedicated file when the mockup set becomes large.

## Mockup Directory

Until the production frontend exists, non-production UI prototypes may live under:

```text
mockups/
  README.md
  package.json
  src/
    data/
    screens/
    components/
  scripts/
```

After `frontend/` exists, production UI belongs in `frontend/`. The `mockups/` directory may remain for SRS/demo-only prototypes if those screens intentionally differ from production code or need isolated visual iteration.

Generated screenshots intended for durable documentation should be committed under:

```text
docs/assets/mockups/
```

or a more specific existing docs asset directory, such as `docs/slides/assets/`, when the image is tied to a slide deck.

Transient screenshot output should be ignored unless the user explicitly asks to preserve it.

## UI Data Contract

Each mockup set must define the real capabilities it uses.

At minimum, include:

- screen names;
- entities shown;
- backend/API fields represented;
- user actions represented;
- calculated values and their backend source;
- empty/loading/error states represented;
- future-state or deferred features, if any.

Mockups must not invent:

- financial calculations;
- AI outputs;
- transaction-derived metrics;
- multi-goal behavior;
- account-linking or bank-sync behavior;
- export/delete behavior;
- analytics or recommendation behavior beyond current deterministic outputs.

If a future-state screen intentionally includes deferred features, label the artifact as future-state and cite the scope decision.

## Visual Reference Handling

The user's rough GoalWise dashboard reference establishes a useful direction:

- app shell with left navigation and main content;
- clean personal-finance dashboard tone;
- goal-first hierarchy;
- summary metrics above detailed content;
- green/blue trust palette;
- readable progress and status treatments.

It does not establish MVP capabilities. In particular, agents must not infer support for multiple active goals, transactions, budget pages, analytics pages, insights pages, accounts pages, XP levels, or rebalancing actions from the reference image alone.

## Screenshot Export Requirements

When screenshot tooling is added, it should:

- render actual UI code in a browser;
- use Playwright or an equivalent browser automation tool;
- export PNG assets at fixed viewport sizes;
- use deterministic mock data from the UI data contract;
- avoid screenshots with loading spinners, transient timestamps, or nondeterministic data;
- produce assets suitable for SRS and slide insertion.

Recommended viewport set:

- desktop: `1600x1000`;
- tablet: `1024x768`;
- mobile: `390x844`.

Use desktop screenshots by default for slides unless the requirement specifically concerns mobile behavior.

## Design Quality Guardrails

GoalWise UI should feel:

- calm and useful;
- financially trustworthy;
- scan-friendly;
- explicit about what is calculated versus entered;
- clear about incomplete setup and missing inputs.

Avoid:

- marketing-page composition for operational app screens;
- fake dashboards filled with unsupported metrics;
- gamification unless explicitly scoped;
- AI-looking magic around money decisions;
- dense decoration that competes with financial comprehension.

## Verification

For docs-only workflow changes:

- Check links and spec index entries.
- Check for contradictions with `SPEC-0007`, `SPEC-0008`, `DESIGN.md`, and ADRs.

For future mockup implementation changes:

- Verify the UI data contract matches available backend/API contracts.
- Run the mockup build or static checks.
- Export screenshots with the documented viewport sizes.
- Inspect screenshots for text overlap, invented data, misleading states, and visual drift.
