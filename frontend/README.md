# GoalWise Frontend

React + Vite frontend code lives under `src/`.

Install dependencies from the repository root:

```sh
make frontend-sync
```

Run the local dev server:

```sh
make frontend-dev
```

Run frontend checks:

```sh
make frontend-check
```

The frontend may format backend-provided values for display, but it must not
duplicate the backend `pace-v1` calculation formulas or official dashboard
metric logic.
