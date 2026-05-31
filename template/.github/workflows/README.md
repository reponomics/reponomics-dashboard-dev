# Template Workflows

This repository is generated from `reponomics-dashboard-dev`. These workflows are template runtime entry points and are intentionally minimal wrappers around `reponomics-dashboard-action`.

- `setup.yml`: bootstraps repository configuration, enables managed workflows, and writes initial setup state.
- `collect.yml.disabled`: scheduled/manual data collection and retained artifact update.
- `publish.yml.disabled`: renders dashboard output from retained artifacts and optional provenance-bound collect runs.
- `rotate-key.yml`: rotates encrypted dashboard state using `DASHBOARD_NEXT_SECRET`.
- `incident-sentinel.yml.disabled`: incident reset and retention safety controls.
- `keepalive.yml.disabled`: periodic activity keepalive to reduce schedule disablement risk.

The `.disabled` suffix is intentional in generated repositories. Setup enables these workflows when configured.
