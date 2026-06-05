# Repository Policy

This project uses a generated template repository instead of long-lived release branches.

## Source Of Truth

Human development happens in `reponomics-dashboard-dev`. This repository owns:

- template workflow stubs
- user-facing template docs
- `template-manifest.yml`
- generated-output tests
- publish tooling for `reponomics-dashboard`
- maintainer docs and ADRs

Maintainer automation targets Python `3.11` as the baseline runtime.

## Generated Template

`reponomics-dashboard` is the shipped template artifact. It should be generated from this repository and contain only the files listed in `template-manifest.yml`.

The generated template is an onboarding shell. It should not contain runtime implementation files, maintainer tests, archived planning docs, virtual environments, or generated local outputs.

## Runtime Action

`reponomics-dashboard-action` is the versioned runtime artifact. It owns collection, artifact restore/upload, schema migration, encryption, README rendering, HTML dashboard rendering, CSV export packaging, update notices, dashboard key rotation, and incident reset behavior.

Generated workflows should call a pinned action ref instead of vendoring runtime internals into every user repository.

## Data Storage Boundary

Retained dashboard data belongs in GitHub Actions artifacts:

- encrypted `dashboard-data.enc` for `strong` and `casual`
- plaintext retained CSV files for private-repository `plain`

Retained dashboard data must not be committed to the generated repository. Dashboard HTML is rendered during `publish` and deployed through Pages artifacts only for encrypted hosted dashboards. Non-hosted publish runs may still upload the rendered dashboard as a downloadable workflow artifact.

## Publication Discipline

Template releases should be generator-driven:

- update source files in `reponomics-dashboard-dev`
- run tests and `make verify`
- inspect `dist/template/`
- validate in a staging consumer when behavior changes
- publish generated output to `reponomics-dashboard`

Direct edits to `reponomics-dashboard` are emergency-only and must be backported to this repository before the next generated publication.

## Workflow Classification

Workflow files in `reponomics-dashboard-dev` are split into two classes:

- template workflow sources live under `template/.github/workflows` with normal `.yml` filenames
- generated template workflows use canonical user-facing filenames: `setup.yml`, `collect.yml.disabled`, `incident-reset.yml.disabled`, `outage-sentinel.yml.disabled`, `keepalive.yml.disabled`, `publish.yml.disabled`, `rotate-key.yml`
- maintainer workflows use the `dev-*.yml` filename prefix

`template-manifest.yml` maps template workflow sources into the generated workflow surface. Maintainer workflows must stay out of the generated template surface.

## Future Demo Repository

A generated demo repository can be useful, but it is not part of the current hardening path. It should be added only after the action/template/staging consumer loop is stable.
