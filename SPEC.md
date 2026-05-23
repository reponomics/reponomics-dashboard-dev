# SPEC

## Project

Build a GitHub template repository that preserves GitHub traffic data in
Actions artifacts and turns it into an optional README snapshot plus a static
HTML dashboard rendered by a versioned runtime action.

## Product Goal

A new GitHub user should be able to:

1. create a repo from the template
2. add `TRAFFIC_TOKEN`
3. choose `strong`, `casual`, or `plain` privacy
4. list the repos they want to track
5. run setup once
6. collect retained traffic history without third-party signup

## Primary User

A first-time or low-experience GitHub builder who may not know Git well, may
not know the traffic endpoints exist, and wants growth signal without setting
up external analytics infrastructure.

## Current V1 Scope

### Included

- views and clones ingestion
- referrer and popular path ingestion
- repository growth counters
- rolling artifact-backed persistence
- twice-daily default collection
- encrypted static HTML dashboard for `strong` and `casual`
- private-repository plaintext artifact mode for `plain`
- optional README snapshot commits via `commit-outputs`
- browser-local CSV export from unlocked encrypted dashboards
- support for public or private tracked repositories

### Excluded From Default Path

- in-repository traffic data storage
- Turso-first storage
- local SQLite-first storage
- multi-backend onboarding
- competitor metrics
- broad CLI/query surface
- advanced setup or migration flows

## Core Architecture

- `reponomics/reponomics-dashboard-action` owns runtime behavior.
- GitHub Actions artifacts hold rolling retained history.
- Normalized CSV is the canonical reporting input.
- Dashboard HTML is rendered during `publish` and deployed through a Pages
  artifact for encrypted hosted dashboards.
- README output is committed only when `commit-outputs` is true.

## Canonical Artifact Payload

- `traffic-log.csv`
- `traffic-daily.csv`
- `traffic-snapshots.csv`
- `traffic-referrers.csv`
- `traffic-paths.csv`
- `repo-metrics.csv`
- `manifest.json`

In `strong` and `casual`, those files are packed into encrypted
`traffic-data.enc` before upload. In `plain`, they are uploaded directly inside
the `traffic-data` artifact and the mode is private-repository only.

## Success Criteria

- one setup run enables the correct workflows
- no database credentials are required
- first collection works with no prior artifact
- second collection preserves prior history
- encrypted dashboard unlocks with `TRAFFIC_DASHBOARD_SECRET`
- unlocked dashboard can export canonical retained CSV as a ZIP
- referrer, path, and repository growth data are captured in v1
