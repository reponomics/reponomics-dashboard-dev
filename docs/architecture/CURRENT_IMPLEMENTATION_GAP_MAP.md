# Reponomics Current Implementation Gap Map

Status: snapshot for dashboard-dev hardening after action `v0.8.0`.

This file tracks the difference between the current implementation and the
remaining work needed to harden the generated dashboard template.

## Authoritative Runtime

`reponomics-dashboard-action` is currently authoritative for runtime behavior.
The template should delegate to `reponomics/reponomics-dashboard-action@v0.8.0`
until a newer accepted release is chosen.

Implemented runtime contract:

- `mode`: `collect`, `publish`, `rotate-key`
- `privacy-mode`: `strong`, `casual`, `plain`
- `strong` and `casual`: encrypted retained artifact plus encrypted hosted
  Pages dashboard during `publish`
- `plain`: private-repository-only retained CSV artifact, no hosted Pages
  dashboard
- `commit-outputs`: commits README output only
- browser-local CSV export from unlocked encrypted dashboards
- canonical artifact payload includes `repo-metrics.csv`

## Dashboard-Dev State

`reponomics-dashboard-dev` owns the generated template source, docs, manifest,
and tests. It should not vendor runtime scripts from the action repo.

Completed in this hardening pass:

- generated workflow stubs align to the `v0.8.0` action input contract
- user-facing docs use the implemented `privacy-mode` model
- unsupported config examples are removed
- stale pre-0.8 architecture drafts are archived
- ADRs remain append-only with current-status notes
- `make verify` passes

## Generated Template State

The generated template should contain only:

- setup, collect, publish, and rotate-key workflows
- `README.md`
- `config.yaml`
- user-facing docs
- basic repository metadata

The generated template should not contain maintainer scripts, tests, ADRs,
archived docs, runtime implementation files, or generated local outputs.

## Remaining Gaps

- Validate the generated template in a real staging consumer with
  `privacy-mode=strong`.
- Exercise browser CSV export from the staging hosted dashboard.
- Exercise key rotation against retained encrypted state.
- Decide whether generated workflows should pin exact release tags such as
  `v0.8.0`, a moving pre-v1 tag, or a future stable `v1` ref.
- Publish the generated template to `reponomics-dashboard` after staging
  validation.

## Known Non-Template Follow-Up

The action runtime remains the place to clean up any lingering old wording in
runtime errors or release materials. Dashboard-dev docs should describe the
current public input contract, not compatibility aliases or historical internal
names.
