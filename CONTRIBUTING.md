# Contributing

This project uses `development` as the integration branch. Do not push implementation work directly to `main`.

## Branching

- Start new work from the latest `development`.
- Use a feature branch for each focused change.
- Keep branches small enough to review clearly.
- Rebase on the latest `development` before opening a PR.
- Use rebase to bring a branch up to date. Do not merge `development` into feature branches.

Suggested branch names:

```text
feature/auth-foundation
feature/pace-engine
fix/snapshot-rounding
docs/readme-guidelines
```

## Pull Requests

- Open PRs back into `development` unless the team explicitly decides otherwise.
- Keep each PR focused on one logical change.
- Include a short summary of what changed and how it was verified.
- Link relevant ADRs, specs, or SRS requirements when the change implements architecture or requirement behavior.
- Do not merge your own PR.
- Prefer a linear history. Rebase feature branches before merge.

## Commit Messages

Use short, consistent commit descriptors:

```text
type: summary
```

Common types:

- `feat`: new user-facing or product behavior
- `fix`: bug fix
- `docs`: documentation-only change
- `test`: tests only
- `refactor`: code restructuring without behavior change
- `chore`: tooling, dependencies, or maintenance

Examples:

```text
docs: add contributor guidelines
feat: add auth session model
fix: correct pace rounding
test: cover cross-user goal access
chore: configure backend linting
```

## Documentation

- Record major architectural decisions as ADRs in `docs/adr/`.
- Record implementation contracts as specs in `docs/specs/`.
- Keep `ARCHITECTURE.md` high level.
- Keep detailed backend/API/calculation design in `DESIGN.md` and specs.

## Verification

Before opening a PR:

- Run the relevant tests or explain why they were not run.
- Check `git status --short` for accidental files.
- Make sure generated caches, secrets, and local environment files are not committed.
- For backend changes, use `make backend-format`, `make backend-lint`, `make backend-typecheck`, and `make backend-test` once the backend scaffold and dev dependencies are installed.

## CI and Testing

Automated CI will be added in a later implementation increment. Until then, each PR should clearly state what was manually checked.

Expected CI gates once implementation begins:

- Backend unit and integration tests.
- Pace-engine golden tests.
- Frontend build and smoke tests.
- Formatting and linting checks.
- Basic security checks for secrets and dependency risk.

PRs should not rely on CI alone. The author is responsible for running the relevant local checks before review.

Backend Python tooling is configured in `backend/pyproject.toml`.
