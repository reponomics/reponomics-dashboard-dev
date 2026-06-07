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

`reponomics-dashboard` is the shipped template artifact. It should be generated from this repository and contain only files sourced through `template-manifest.yml`. The template source tree lives under `template/`; generated paths strip that leading prefix unless an explicit `source`/`target` mapping is used.

The generated template is an onboarding shell. It should not contain runtime implementation files, maintainer tests, archived planning docs, virtual environments, or generated local outputs.

Top-level community-health files such as `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, and `SUPPORT.md` are template-owned generated files. They should be sourced from `template/` and mapped through `template-manifest.yml`, not copied from this development repository's own community docs. Action managed docs sync has a narrower boundary: it writes only `docs/reponomics/` in generated repositories.

The generated template should also ship an initial `docs/reponomics/` snapshot from the accepted `reponomics-dashboard-action` release. That snapshot belongs under `template/docs/reponomics/` in this repository and should be refreshed by action-release sync, not by direct commits to `reponomics-dashboard`.

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

The maintainer release cadence is documented in [Template Release Protocol](TEMPLATE_RELEASE_PROTOCOL.md). In short, accepting an action release into dashboard-dev and publishing a dashboard-dev/template release are separate decisions. Dashboard-dev releases use semantic versioning for the generated template, and intentional publications should be requested with an explicit `Release-As` trailer.

## Workflow Classification

Workflow files in `reponomics-dashboard-dev` are split into two classes:

- template workflow sources live under `template/.github/workflows` with normal `.yml` filenames
- generated template workflows use canonical user-facing filenames: `setup.yml`, `collect.yml`, `incident-reset.yml`, `keepalive.yml`, `publish.yml`, `rotate-key.yml`
- maintainer workflows use the `dev-*.yml` filename prefix

`template-manifest.yml` maps template workflow sources into the generated workflow surface, normally by stripping the leading `template/` prefix. Maintainer workflows must stay out of the generated template surface.

## Future Demo Repository

A generated demo repository can be useful, but it is not part of the current hardening path. It should be added only after the action/template/staging consumer loop is stable.
