# Generated Repository Model

Status: current for the v0.8 template hardening pass.

This project treats repository boundaries as product boundaries.

## Repositories

`reponomics-dashboard-dev` is the editable source of truth for the generated
dashboard template. It contains maintainer docs, template workflow stubs,
`template-manifest.yml`, tests, release tooling, and generated-output checks.

`reponomics-dashboard` is the shipped template repository for **Use this
template**. It is generated from `reponomics-dashboard-dev` and should contain
only the files listed in `template-manifest.yml`.

`reponomics-dashboard-action` is the versioned runtime action. It owns
collection, artifact restore/upload, schema migration, encryption, README
rendering, HTML dashboard rendering, CSV export packaging, key rotation, and
release notices.

`reponomics-dashboard-demo` is not part of the current release path. A demo can
be reintroduced after a staging consumer has validated the generated template
against the released action.

## Generated Template Surface

The generated template intentionally includes only:

- workflow stubs for setup, collection, publication, scheduled workflow keepalive, incident response, and key rotation
- `README.md`
- `config.yaml`
- user-facing docs under `docs/`
- repository metadata such as `.gitignore` and `LICENSE`

It intentionally excludes maintainer scripts, tests, ADRs, archived planning
docs, `dist/`, virtual environments, and runtime implementation files.

Template workflow sources live under `template/.github/workflows` so this repository's live `.github/workflows` directory contains only maintainer workflows. `template-manifest.yml` is the source-to-template contract; it maps those source workflows into the generated workflow filenames copied to `reponomics-dashboard`. Changes to the generated surface should be made by updating the manifest and tests, then building the generated output.

## Runtime Contract

Generated workflows delegate to:

```yaml
uses: reponomics/reponomics-dashboard-action@v0.16.0
```

The action input contract used by this template is:

- `mode`: `collect`, `publish`, or `rotate-key`
- `collection-token`
- `github-token`
- `dashboard-secret`
- `dashboard-next-secret`
- `privacy-mode`: `strong`, `casual`, or `plain`
- `config-path`
- `retention-days`
- `generate-readme`

The template does not vendor runtime scripts or renderer assets.

## Data And Output Model

Retained dashboard data lives in the `dashboard-data` GitHub Actions artifact.

- `strong` and `casual` store encrypted retained data as `dashboard-data.enc`.
- `plain` stores retained CSV files directly and is private-repository only.
- Hosted dashboard HTML is rendered during `publish` and deployed as a GitHub
  Pages artifact for `strong` and `casual`.
- setup commits a static README; metric README output is committed only when `generate-readme` is true in a private repository.
- CSV export is browser-local after encrypted dashboard unlock.

No retained dashboard data CSV is committed to the generated repository.

## Maintainer Gates

Before publishing a generated template update:

- run the generated-template test suite
- build and verify `dist/template/`
- inspect the generated workflows for the pinned action ref
- verify user-facing docs do not reference maintainer-only files
- validate the generated template in a staging consumer before broad release
