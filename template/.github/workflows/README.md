# Template Workflows

> [!WARNING]
> Pre-release placeholder workflow inventory.

Repository context:

- In `reponomics/reponomics-dashboard`, these files are generated from `reponomics-dashboard-dev`.
- In repositories created from the template, these are the consumer workflow entry points.

These workflows are intentionally minimal wrappers around `reponomics-dashboard-action`.

- `setup.yml`: bootstraps repository configuration, enables managed workflows, and writes initial setup state.
- `collect.yml`: scheduled/manual data collection and retained artifact update.
- `publish.yml`: renders dashboard output from retained artifacts and optional provenance-bound collect runs.
- `rotate-key.yml`: rotates encrypted dashboard state using `DASHBOARD_NEXT_SECRET`.
- `incident-sentinel.yml`: incident reset and retention safety controls.
- `keepalive.yml`: periodic activity keepalive to reduce schedule disablement risk.

Before setup, guarded workflows no-op and write a summary telling users to run setup first.
