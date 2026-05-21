# Reponomics Dashboard Documentation

Welcome to your personal GitHub BI dashboard.

Reponomics is a GitHub-native traffic dashboard. It collects views, clones, top
referrers, popular paths, and aggregate repository counters, then renders and
publishes static dashboard output during the `publish` workflow.

## Repository Model

This template repository is intentionally thin. The workflows call
`reponomics/reponomics-action@main`, which owns collection, artifact handling,
schema migration, encryption, README rendering, dashboard rendering, and key
rotation behavior.

Your repository owns:

- `config.yaml`
- any settings you copy into `config.yaml` from `docs/config.example.yaml`
- repository secrets
- workflow schedule and permissions
- retained `traffic-data` artifacts
- dashboard shell files such as the placeholder `docs/index.html`
- committed README output when README publishing is enabled
- the pinned action version

## Configuration

`config.yaml` is the active configuration for this repository. It is
user-owned: normal collection and publication runs read it, but should not
silently rewrite it.

`docs/config.example.yaml` is a reference file showing the current supported
configuration shape. When Reponomics adds compatible optional settings, the
example can be updated and release notes can point to the relevant snippet. You
only need to copy settings into `config.yaml` when you want to override the
runtime default.

Missing optional keys use runtime defaults. Explicit keys in `config.yaml` are
treated as your choices.

## Storage

The canonical data store is the `traffic-data` GitHub Actions artifact.

In plain mode, the artifact contains normalized CSV files. In encrypted mode,
the artifact contains `traffic-data.enc`, encrypted with
`TRAFFIC_DASHBOARD_SECRET`.

Git history is used for repository configuration, workflow shells, and dashboard
shell files, not as the analytics database. Retained traffic data is not
committed to the repository.

## Outputs

During `publish`, Reponomics can render:

- `README.md`
- a hosted Pages dashboard artifact
- `dist/dashboard-standalone.html` as a workflow artifact when Pages mode is
  plain

## Offline Viewing

The generated dashboard is not committed to this repository. This keeps retained traffic data out of git history, but it also means you download dashboard output from the relevant `publish` workflow artifact rather than from the repository tree.

After a successful **Publish Reponomics dashboard** run, open the workflow run's **Summary** page and download the artifact before it expires:

- For plain dashboard output, download `dashboard-standalone` and open `dashboard-standalone.html`.
- For encrypted dashboard output, download the GitHub Pages artifact, extract it, and open `index.html`. Use the same dashboard key that unlocks the hosted Pages dashboard.

Artifact availability follows the workflow's retention setting.

## Modes

`readme-dashboard`:

- `disabled`: README does not publish metrics
- `enabled`: README shows rich static metrics and SVG charts

`pages-dashboard`:

- `encrypted`: dashboard data is encrypted and unlocked in the browser with
  your dashboard key
- `plain`: dashboard data is written unencrypted
- `disabled`: dashboard page is a placeholder

`artifact-security-mode`:

- `auto`: conservative default; encrypts public-repo artifacts unless the user
  intentionally chooses a fully open/plain profile
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

Hosted Pages setup modes configure GitHub Pages to publish from the Reponomics
publish workflow. That workflow renders the dashboard shell and uploads it as a
GitHub Pages artifact; retained traffic data remains in the `traffic-data`
Actions artifact.

> [!ALERT]
> Unless you have a GitHub Enterprise account, then
> whether your repository is public or private, **your GitHub Pages site will
> be published to the open internet.**

Furthermore, unless you configure a custom domain, its URL will be entirely predictable. The only way to guarantee some mmeasure of privacy is by encrypting the public page with a `TRAFFIC_DASHBOARD_SECRET`. When you do this, anyone who visits the page will be unable to view the actual data/dashboard unless they have that secret.
