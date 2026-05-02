# Reponomics Dashboard Documentation

Reponomics is a GitHub-native traffic dashboard. It collects views, clones, top
referrers, popular paths, and aggregate repository counters, then renders
static outputs in this repository.

## Repository Model

This template repository is intentionally thin. The workflows call
`reponomics/reponomics-action@main`, which owns collection, artifact handling,
schema migration, encryption, README rendering, dashboard rendering, and key
rotation behavior.

Your repository owns:

- `config.yaml`
- repository secrets
- workflow schedule and permissions
- retained `traffic-data` artifacts
- committed outputs such as `README.md`, `docs/index.html`, and `docs/assets/`
- the pinned action version

## Storage

The canonical data store is the `traffic-data` GitHub Actions artifact.

In plain mode, the artifact contains normalized CSV files. In encrypted mode,
the artifact contains `traffic-data.enc`, encrypted with
`TRAFFIC_DASHBOARD_SECRET`.

Git history is used only for published outputs, not as the analytics database.

## Outputs

Reponomics can write:

- `README.md`
- `docs/index.html`
- `docs/assets/*`
- `dist/dashboard-standalone.html` as a workflow artifact when Pages mode is
  public

## Modes

`readme-dashboard`:

- `disabled`: README does not publish metrics
- `metrics_summary`: README shows summary metrics and SVG charts

`pages-dashboard`:

- `encrypted`: dashboard data is encrypted and unlocked in the browser with
  your dashboard key
- `public`: dashboard data is written in plaintext
- `disabled`: dashboard page is a placeholder

`artifact-security-mode`:

- `auto`: private default; encrypts public-repo artifacts unless Pages is
  intentionally public
- `encrypted`: always encrypt retained artifact data
- `plain`: upload normalized CSV files directly

## Key Rotation

1. Generate and save a new dashboard key.
2. Add it as `TRAFFIC_DASHBOARD_NEXT_SECRET`.
3. Run **Actions -> Rotate Reponomics dashboard key -> Run workflow**.
4. Confirm the dashboard opens with the new key.
5. Replace `TRAFFIC_DASHBOARD_SECRET` with the new key.
6. Delete `TRAFFIC_DASHBOARD_NEXT_SECRET`.

Normal collection refuses to run while `TRAFFIC_DASHBOARD_NEXT_SECRET` is set,
so rotation cannot be left half-finished unnoticed.

## GitHub Pages

To host `docs/index.html`, set **Settings -> Pages -> Source** to **Deploy
from a branch**, choose branch `main`, folder `/docs`, then save.

GitHub Pages visibility depends on your GitHub plan and repository settings.
Encrypted dashboard mode protects the dashboard data payload, but it does not
make a compromised hosting surface trustworthy.
