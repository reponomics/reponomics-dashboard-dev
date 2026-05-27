# Dashboard Template Hardening Checklist

Status: action `v0.12.1` published; dashboard-dev template hardening in
progress.

## Current Contract

- [x] Runtime action is `reponomics/reponomics-dashboard-action`.
- [x] Generated template delegates collection, publishing, CSV export, and key
  rotation to the action.
- [x] Retained traffic data is stored only in GitHub Actions artifacts.
- [x] Dashboard HTML is rendered during `publish` and deployed as a Pages
  artifact for encrypted modes.
- [x] README output is committed only when `commit-outputs` is true.
- [x] Privacy modes are `strong`, `casual`, and `plain`.
- [x] `plain` is private-repository only and does not publish a hosted Pages
  dashboard.
- [x] Encrypted dashboards support browser-local CSV export after unlock.

## Dashboard-Dev Hardening

- [x] Align generated workflow stubs with action `v0.12.1`.
- [x] Replace obsolete README/Pages/artifact mode docs with `privacy-mode`
  docs.
- [x] Remove unsupported `data_families` config examples.
- [x] Archive pre-0.8 speculative design docs.
- [x] Keep ADRs append-only and add current implementation notes.
- [x] Build and verify `dist/template/`.
- [ ] Validate the generated template in a staging consumer repository.
- [ ] Publish the generated template to `reponomics-dashboard`.

## Staging Consumer Checks

- [ ] Run setup with `privacy-mode=strong`.
- [ ] Confirm setup enables `collect.yml` and `publish.yml`.
- [ ] Confirm collection creates/updates the `dashboard-data` artifact.
- [ ] Confirm publish deploys an encrypted Pages artifact.
- [ ] Unlock the hosted dashboard with `DASHBOARD_SECRET_DO_NOT_REPLACE`.
- [ ] Export CSV from the browser and verify the downloaded ZIP.
- [ ] Rotate to `DASHBOARD_NEXT_SECRET` and confirm old data survives.
- [ ] Run a private-repository `plain` smoke test if that mode remains in the
  release surface.

## Release Hygiene

- [ ] Keep generated workflows pinned to an accepted action release ref.
- [ ] Update docs when action inputs or output semantics change.
- [ ] Validate release-notice metadata before publishing action releases.
- [ ] Keep archived docs out of the generated template.
- [ ] Avoid direct human commits to the generated template repository except
  emergency repairs that are backported to dashboard-dev.
