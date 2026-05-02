# SPEC

## Project

Build a new GitHub template repository that preserves GitHub traffic data and
turns it into a README snapshot and a static HTML dashboard.

## Product Goal

A new GitHub user should be able to:

1. create a repo from the template
2. add one token
3. list the repos they want to track
4. run one workflow
5. get a README snapshot and dashboard without third-party signup

## Primary User

A first-time or low-experience GitHub builder who may not know Git well, may
not know the traffic endpoints exist, and wants growth signal without setting
up external analytics infrastructure.

## V1 Scope

### Included

- views and clones ingestion
- referrer and popular path ingestion
- rolling artifact-backed persistence
- twice-daily default collection
- static HTML dashboard
- README snapshot
- support for public or private tracked repositories

### Excluded From Default Path

- Turso-first storage
- local SQLite-first storage
- multi-backend onboarding
- competitor metrics
- broad CLI/query surface
- advanced setup or migration flows

## Core Architecture

- Git commits published outputs
- GitHub Actions artifacts hold rolling history
- normalized CSV is the canonical reporting input
- README and dashboard are generated from the same daily materialized dataset

## Canonical Artifact Payload

- `traffic-log.csv`
- `traffic-daily.csv`
- `traffic-snapshots.csv`
- `traffic-referrers.csv`
- `traffic-paths.csv`
- `manifest.json`

## Success Criteria

- one-token onboarding succeeds
- no DB credentials are required
- first run works with no prior artifact
- second run preserves prior history
- dashboard works as static HTML
- referrer and path data are captured in v1
