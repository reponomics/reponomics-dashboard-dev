# Reponomics Repository Specs

Version: 0.1 intended design

This document gives the intended contract for each primary repository. The
`reponomics-dashboard` section is a spec for a generated artifact, not a normal
human-maintained repository.

## `reponomics-dashboard-dev`

Role:

- Source-of-truth workspace for the Reponomics dashboard template product.
- Builds and publishes the generated `reponomics-dashboard` artifact.
- Owns template workflow shells, onboarding docs, privacy UX docs, release
  policy, and generated-template tests.

Primary users:

- Reponomics maintainers.
- Release automation.

Must contain:

- template source files
- `template-manifest.yml`
- tests that prove the generated template is thin
- publish tooling for `reponomics-dashboard`
- repository policy tooling
- architecture and release docs

Must not contain:

- product traffic data
- user dashboard secrets
- action runtime source, except local fixtures if explicitly needed for
  contract tests
- generated demo data as source of truth

Required credentials:

- Normal verification: no product secrets.
- Publishing generated `reponomics-dashboard`: a credential with write access
  to `reponomics/reponomics-dashboard`.
- Repository policy enforcement: a credential with enough repository
  administration permissions to set template status, workflow state, security
  settings, and branch/repository options.

Credential strategy:

- Short term: maintainer local auth or a fine-grained org PAT restricted to the
  Reponomics repositories and the specific operations needed.
- Preferred long term: a Reponomics GitHub App installed on the org, with
  narrowly scoped repository permissions. The app gives better auditability,
  easier rotation, and clearer separation between personal credentials and
  release automation.
- Avoid broad personal PATs for unattended release operations once the public
  launch process exists.

Workflows:

- `Maintainer CI`: verify generated template output and contract tests.
- `Publish generated template`: manual or protected release workflow that
  builds `dist/template/` and publishes it to `reponomics-dashboard`.
- `Enforce repository policy`: manual/dry-run first workflow for repo settings.

Outputs:

- `dist/template/`
- publish commit to `reponomics-dashboard`
- optional repository policy report

Non-goals:

- Running collection for its own traffic.
- Storing user data.
- Publishing dashboard UI directly to users outside the generated template and
  runtime action path.

## `reponomics-dashboard`

Role:

- Generated GitHub template artifact.
- Copied into user repositories through **Use this template**.

This repository should be treated as the published form of `dist/template/`.
Direct edits are emergency-only and must be backported to
`reponomics-dashboard-dev`.

Must contain:

- onboarding `README.md`
- `config.yaml`
- `docs/README.md`
- `docs/SECURE_DASHBOARD_KEY.md`
- placeholder `docs/index.html`
- `.github/workflows/setup.yml`
- `.github/workflows/collect.yml.disabled`
- `.github/workflows/rotate-key.yml`
- license and ignore rules

Must not contain:

- Python runtime scripts
- runtime dependencies
- maintainer docs
- tests
- generated demo CSV
- generated release tooling
- private Reponomics planning material

Required credentials:

- The template repository itself should not require product secrets.
- User-created repositories need their own secrets after template creation.

Workflows in the template repository:

- Workflow files exist because they must be copied into user repositories.
- Product workflows should not be used to collect `reponomics-dashboard` traffic
  itself.
- Repository policy may disable or restrict runnable product workflows in this
  repository while keeping the files present.

Generated artifact tests:

- File set matches `template-manifest.yml`.
- No action-owned runtime internals are present.
- Workflows call a pinned `reponomics-action` ref.
- `collect.yml` is absent; `collect.yml.disabled` is present.

## User-created repository from `reponomics-dashboard`

Role:

- Actual product consumer.
- Owns config, secrets, retained artifacts, generated outputs, and action ref.

Required secrets:

- `TRAFFIC_TOKEN`: required to collect GitHub traffic and repository metadata.
- `TRAFFIC_DASHBOARD_SECRET`: required when encrypted dashboard output or
  encrypted retained artifacts are selected.
- `TRAFFIC_DASHBOARD_NEXT_SECRET`: temporary secret for key rotation only.

Optional credentials:

- `GITHUB_TOKEN`: available by default in Actions for repository operations.
- A custom repository token only if the default workflow token is insufficient
  for the user's chosen workflow.

Workflows:

- Setup configures modes and enables collection.
- Collection maintains retained data and, depending on the chosen mode,
  publishes selected outputs.
- Rotation re-encrypts retained state and dashboard output without collecting.

Outputs:

- retained `traffic-data` artifact
- `README.md`
- `docs/index.html`
- `docs/assets/*`
- optional standalone dashboard artifact

## `reponomics-action`

Role:

- Runtime engine and update channel.
- Owns collection, artifact restore/upload, encryption, schema handling,
  rendering, publication behavior, and key rotation.

Must contain:

- `action.yml`
- runtime source
- runtime tests
- action documentation
- release/versioning metadata

Must not contain:

- user secrets
- user retained artifacts
- generated dashboard-template artifacts
- demo data as production state

Required credentials:

- Normal CI: none beyond default CI permissions.
- Release: maintainer or app credential able to create tags/releases.
- Live integration validation: test repository secrets owned by the staging
  consumer, not by the action repo.

Workflows:

- Runtime test CI.
- Action metadata validation.
- Release/tag workflow once public versioning policy is accepted.

Action modes:

- `collect`
- `rotate-key`
- `publish`, under consideration

Outputs:

- action metadata outputs for workflow summaries and downstream automation
- files/artifacts in the caller repository

Non-goals:

- Owning user configuration.
- Mutating user repository secrets.
- Serving as the template source of truth.

## Umbrella Product Repository: `reponomics` (Proposed)

Role:

- Public product home and community surface.
- The repository people are most likely to star, share, watch, and discuss.
- Entry point for docs, roadmap, support, examples, and links to the install
  template.

Why it should exist:

- Template repositories are installation artifacts; they are not ideal product
  home pages.
- Users may be reluctant to star a template repo that exists mostly to be
  copied.
- A stable umbrella repo gives Reponomics a durable public URL even if the
  template/action/demo repository structure evolves.

Must contain:

- product README
- installation links
- architecture overview
- privacy model summary
- roadmap and issues/discussions policy
- links to `reponomics-dashboard`, `reponomics-action`, demo, docs, and release
  notes

Must not contain:

- generated template source of truth
- runtime action implementation
- user data
- generated demo data as source of truth

Workflows:

- docs/link validation
- release note aggregation, if useful
- no product collection by default

Secrets:

- none required for normal operation

Open decisions:

- whether the umbrella repo is created now or after the first live staging
  validation
- whether GitHub Discussions live there
- whether issues live there or stay split by component repo
- whether public docs are served from the umbrella repo, the template repo, or a
  separate site

