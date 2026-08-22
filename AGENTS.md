# Agent Guidelines

These instructions apply to coding agents working in this repository.

## Start Here

Before making changes, read:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [README.md](README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [DESIGN.md](DESIGN.md)
- [Product context](docs/PRODUCT_CONTEXT.md)

For architecture or behavior changes, also consult:

- [ADRs](docs/adr/README.md)
- [Implementation specs](docs/specs/README.md)
- [SRS v2.0](docs/srs/goal-wise-srs-v2.md)
- [SRS v1.0 historical baseline](docs/srs/goal-wise-srs-v1.md)
- [MVP scope mapping](docs/specs/0007-srs-traceability-and-mvp-scope.md)

## Architectural Discipline

GoalWise is a progressive MVP/PDR subset of the broader SRS. Do not silently expand scope.

Current MVP priorities:

- One active savings goal.
- Manual financial assumptions.
- Deterministic `pace-v1` calculation.
- Immutable calculation snapshots.
- Backend-owned dashboard values.
- User-owned data isolation.
- AI-free financial core.

Deferred areas include CSV import, AI summaries, export/delete, background scheduling, and multi-goal support. Do not implement deferred areas unless the user explicitly asks and the scope docs are updated.

## Drift Warnings

Warn the user before making a change that drifts from existing architecture decisions or specs.

Examples of drift:

- Moving safe-to-spend calculation into the frontend.
- Letting AI calculate or override financial outputs.
- Storing money as floating-point values.
- Returning `403` for cross-user private resource access instead of `404`.
- Mutating calculation snapshots after insert.
- Adding CSV, AI, export/delete, scheduler, or multi-goal behavior without updating scope docs.
- Changing auth/session/CSRF behavior without updating the auth spec.

When drift is intentional, update the relevant ADR, spec, and plan in the same change.

## Documentation Updates

If a change affects architecture, behavior, security, API contracts, data shape, deployment, or MVP scope:

- Update the relevant spec in `docs/specs/`.
- Add or update an ADR in `docs/adr/` when the "why" changes.
- Update `DESIGN.md` when backend/data/API/calculation design changes.
- Update `ARCHITECTURE.md` only for high-level system changes.
- Update the MVP scope mapping when SRS implementation status changes.

ADRs explain why. Specs define exactly how.

## Implementation Boundaries

- The backend is the source of truth for financial calculations and official dashboard metrics.
- The React frontend may format and visualize backend values, but must not duplicate pace-engine formulas.
- The pace engine must remain deterministic and independent of FastAPI, SQLAlchemy, sessions, frontend code, and AI providers.
- Store money as integer cents.
- Store timestamps in UTC and date-only values in the user's local calendar semantics.
- Use server-side ownership checks for every protected user-owned resource.
- Keep raw transaction descriptions out of immutable calculation snapshots.

## Git Workflow

Follow [CONTRIBUTING.md](CONTRIBUTING.md):

- Branch from `development`.
- Rebase on latest `development`; do not merge `development` into feature branches.
- Open PRs back into `development` unless instructed otherwise.
- Do not merge your own PR.
- Use consistent commit descriptors such as `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, and `chore:`.

## UI Mockup Workflow

Follow [SPEC-0009](docs/specs/0009-ui-mockup-and-screenshot-workflow.md) before creating UI mockups, frontend screenshots, or SRS visual assets.

Treat `docs/PRODUCT_CONTEXT.md`, the SRS scope mapping, ADRs, specs, and backend contracts as product truth. Visual references may guide layout, tone, and hierarchy, but they do not define supported capabilities.

Agents must warn the user before:

- inventing metrics, entities, filters, actions, or navigation not represented in the specs or backend contracts;
- showing deferred features as current MVP behavior;
- presenting AI as calculating or overriding financial results;
- using standalone generated UI images when the purpose is an SRS or slide screenshot of the app.

Prefer implemented UI rendered in a browser, then exported to deterministic PNGs with fixed viewport sizes. Use image generation only for illustrations or visual concepts, not for authoritative app screenshots.

## Release Operations

Follow [docs/release-process.md](docs/release-process.md) for release policy. Use this section for agent execution details.

Use a separate worktree for release, tag, and GitHub Release operations so active implementation work in the base worktree is not disturbed.

Recommended setup:

```bash
git fetch origin --tags
git worktree add --detach /private/tmp/goal-wise-release-worktree origin/development
```

Before opening a release PR:

- Verify the worktree points at latest `origin/development`.
- Run `make backend-sync` if the worktree has a fresh virtual environment.
- Run `make backend-check`.
- Check for an existing `development -> main` PR.
- Open the release PR from `development` to `main`.
- Format the PR body using the release-candidate structure in `docs/release-process.md`.

Before tagging:

- Confirm the release PR is merged.
- Fetch latest `main` and tags.
- Confirm the intended tag does not already exist.
- Tag the merged `main` commit, not `development` and not a feature branch.
- Prefer annotated tags.

Tag command pattern:

```bash
git fetch origin --tags
git tag -a vX.Y.Z origin/main -m "vX.Y.Z - <milestone name>"
git push origin vX.Y.Z
```

Before creating a GitHub Release:

- Confirm the tag exists on the remote.
- Confirm a GitHub Release does not already exist for that tag.
- Use cleaned release notes from the merged release PR.
- Do not include the "Release Candidate" instruction block in the final GitHub Release notes.

GitHub Release command pattern:

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - <milestone name>" \
  --notes "<release notes>"
```

After creating the release, verify:

```bash
gh release view vX.Y.Z --json tagName,name,url,isDraft,isPrerelease,targetCommitish
```

## Verification

Run relevant checks before finishing a change. If tests or checks are not available yet, state what was reviewed manually.

For docs-only changes:

- Check links and indexes.
- Check Mermaid diagrams render when changed.
- Check for stale or contradictory wording.

For implementation changes:

- Add or update tests that match the risk of the change.
- Prioritize pace-engine golden tests for calculation behavior.
- Include cross-user access tests for protected resources.
- Include auth/session/CSRF tests for authentication changes.
