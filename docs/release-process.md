# Release Process

GoalWise uses `development` as the integration branch and `main` as the release/demo-ready branch.

## Branch Roles

- `development`: integration branch for completed feature work.
- `main`: stable branch used for releases and demos.
- `feature/*`, `fix/*`, `docs/*`, `chore/*`: focused branches cut from `development`.

Do not create `release/*` branches for the current MVP workflow. Add release branches only if the project needs a separate stabilization or hotfix line.

## Standard Release Flow

1. Merge focused feature PRs into `development`.
2. Rebase or update release-bound work on the latest `development`.
3. Open a PR from `development` into `main` when the current milestone is ready.
4. Use the PR as the release review and verification checkpoint.
5. Merge the PR into `main`.
6. Create a Git tag on the resulting `main` commit.
7. Create a GitHub Release from that tag.

```text
feature branch -> development -> main -> tag -> GitHub Release
```

## Version Tags

Use semantic-version-style tags:

```text
v0.1.0
v0.2.0
v1.0.0
```

Before the full MVP is complete, prefer `v0.x.0` milestone releases. Reserve `v1.0.0` for the course/demo-ready MVP.

## Release Notes

Release notes should be human-readable and based on:

- merged PR summaries;
- meaningful commit messages;
- verification results;
- known limitations or deferred scope.

Recommended structure:

```md
## Summary
- ...

## Verification
- ...

## Notes
- ...
```

## When to Add Release Branches

Introduce `release/*` branches only when one of these becomes true:

- release validation takes long enough that normal feature work must continue separately;
- hotfixes need to be made against a released version while `development` has moved on;
- multiple released versions must be supported at the same time;
- CI/CD or deployment environments require a frozen release-candidate branch.

Until then, use the `development -> main` PR as the release checkpoint.
