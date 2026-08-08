# GoalWise Backend

Backend Python tooling is configured in `pyproject.toml`.

Create the project virtual environment and install development dependencies from the
repository root:

```sh
uv venv
make backend-sync
```

Common commands from the repository root:

```sh
make backend-format
make backend-lint
make backend-typecheck
make backend-test
make backend-check
```

The root `Makefile` runs backend tools through `uv` from the backend directory while
pointing uv at the repository-root `.venv`, so checks use the project environment
instead of the global Python installation.
