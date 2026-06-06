# Generated Repository Model

Status: current for the action `v0.16.0` template hardening pass.

This project treats repository boundaries as product boundaries.

## Repositories

`reponomics-dashboard-dev` is the editable source of truth for the generated dashboard template. It contains maintainer docs, template workflow stubs, `template-manifest.yml`, tests, release tooling, and generated-output checks.

`reponomics-dashboard` is the shipped template repository for **Use this template**. It is generated from `reponomics-dashboard-dev` and should contain only the files listed in `template-manifest.yml`.

`reponomics-dashboard-action` is the versioned runtime action. It owns collection, artifact restore/upload, schema migration, encryption, README rendering, HTML dashboard rendering, CSV export packaging, key rotation, managed local documentation sync, and release notices.

`reponomics-dashboard-demo` is not part of the current release path. A demo can be reintroduced after a staging consumer has validated the generated template against the released action.

## Generated Template Surface

The generated template intentionally includes only:

- workflow stubs for setup, collection, publication, scheduled workflow keepalive, incident response, and key rotation
- `README.md`
- `config.yaml`
- user-facing docs under `docs/`
- top-level community-health placeholder docs such as `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `SUPPORT.md`
- an initial Reponomics-managed local docs snapshot under `docs/reponomics/`, generated from the accepted action release and updated after docs sync runs
- repository metadata such as `.gitignore` and `LICENSE`

It intentionally excludes maintainer scripts, tests, ADRs, archived planning docs, `dist/`, virtual environments, and runtime implementation files.

Template workflow sources live under `template/.github/workflows` so this repository's live `.github/workflows` directory contains only maintainer workflows. `template-manifest.yml` is the source-to-template contract; it maps those source workflows into the generated workflow filenames copied to `reponomics-dashboard`. Changes to the generated surface should be made by updating the manifest and tests, then building the generated output.

Top-level community-health files are template-owned shipped files. They are generated from sources in `template/` and may intentionally differ from this development repository's own community docs. Action-owned managed docs sync is a separate mechanism: it may write only `docs/reponomics/` in generated repositories, and it should not be expanded into a top-level community-health-file updater without a new design decision.

The `template/docs/reponomics/` source directory is a generated snapshot of the accepted `reponomics-dashboard-action` managed-docs bundle. Action-release sync refreshes that snapshot from `template-action-release.yml` so the public template is browseable before any workflow runs. Runtime `docs-sync` remains the owner of later updates in generated/user repositories.

## Runtime Contract

Generated workflows delegate to:

```yaml
uses: reponomics/reponomics-dashboard-action@v0.20.1
```

Collection also records the accepted action tag and resolved action commit SHA in a `reponomics-collect-provenance` artifact when publication is enabled. The automatic publish workflow downloads that artifact, restores `dashboard-data` from the recorded collect workflow run, checks out the recorded repository SHA, checks out `reponomics-dashboard-action` at the recorded commit, and runs the action as a local action. This keeps automatic publish locked to the same action/data contract as the collect run that produced the retained artifact.

The action input contract used by this template is:

- `mode`: `collect`, `publish`, `rotate-key`, or `docs-sync`
- `collection-token`
- `github-token`
- `dashboard-secret`
- `dashboard-next-secret`
- `privacy-mode`: `strong`, `casual`, or `plain`
- `config-path`
- `retention-days`
- `generate-readme`
- `allow-docs-sync`

The template does not vendor runtime scripts or renderer assets.

## Data And Output Model

Retained dashboard data lives in the `dashboard-data` GitHub Actions artifact.

- `strong` and `casual` store encrypted retained data as `dashboard-data.enc`.
- `plain` stores retained CSV files directly and is private-repository only.
- Hosted dashboard HTML is rendered during `publish` and deployed as a GitHub Pages artifact for `strong` and `casual` only when hosted publication is enabled. Otherwise, the rendered dashboard is uploaded as a downloadable workflow artifact.
- Automatic publish consumes collect provenance instead of the latest default branch action ref, so action upgrades cannot reinterpret an older collection artifact.
- setup commits a static README; metric README output is committed only when `generate-readme` is true in a private repository.
- the generated template starts with the accepted action release's managed local documentation under `docs/reponomics/`.
- `docs-sync` runs before collection and commits managed local documentation updates only under `docs/reponomics/`; missing write permission is advisory by default.
- top-level community-health docs are not managed by `docs-sync`.
- CSV export is browser-local after encrypted dashboard unlock.

No retained dashboard data CSV is committed to the generated repository.

## Maintainer Gates

Before publishing a generated template update:

- run the generated-template test suite
- build and verify `dist/template/`
- inspect the generated workflows for the pinned action ref
- verify user-facing docs do not reference maintainer-only files
- validate the generated template in a staging consumer before broad release
