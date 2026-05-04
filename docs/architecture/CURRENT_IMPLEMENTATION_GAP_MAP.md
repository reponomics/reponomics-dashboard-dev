# Reponomics Current Implementation Gap Map

Version: 1.0 snapshot against intended design

This document describes the current implementation state so it can be compared
against the intended architecture. Unlike the other architecture documents, this
file is intentionally implementation-specific.

## Current Repository State

`reponomics-action`:

- has an initial composite action on `main`
- supports `mode: collect`, `mode: publish`, and `mode: rotate-key` locally
- contains copied Python runtime scripts
- has local fixture tests
- has split `traffic-token` and `github-token` inputs locally
- uses `pages-dashboard: plain` while accepting `public` as a deprecated alias
- uses `readme-dashboard: enabled` while accepting `metrics_summary` as a
  deprecated alias
- exposes `allow-weak-dashboard-secret`

`reponomics-dashboard-dev`:

- is pushed on `main`
- contains the generated-template source and manifest
- builds a thin `dist/template/`
- has tests enforcing that the generated template excludes runtime internals
- contains this architecture documentation

`reponomics-dashboard`:

- is generated from `reponomics-dashboard-dev`
- is pushed on `main`
- is marked as a GitHub template repository
- currently references `reponomics/reponomics-action@main`

Umbrella product repo:

- not created or populated as part of this architecture snapshot
- intended as the public star/share/discussion surface

## Known Contract Gaps

### Token Boundary

Intended contract:

- `traffic-token` is for GitHub traffic and repository metadata APIs.
- `github-token` is for artifact and repository workflow operations.

Current state:

- local action changes split the inputs, but live staging has not validated the
  boundary yet

Risk:

- users and maintainers may misunderstand which permissions are needed and why.

Likely fix:

- validate the split in a generated staging repository

### Dashboard Disclosure Naming

Intended contract:

- use `plain` to mean unencrypted dashboard output
- reserve `public` for repository visibility or public product release

Current state:

- local action and template changes use `pages-dashboard: plain`; `public`
  remains only as a deprecated pre-release alias in the action

Risk:

- users may confuse repository visibility with dashboard encryption state.

Likely fix:

- validate generated workflows and docs no longer present `public` as the user
  input for unencrypted output

### Setup Workflow Scope

Intended contract:

- setup validates selected modes and enables collection and publication
  workflows
- setup should not own collection semantics
- setup stops before first collection, after validating secrets and explaining
  the next action

Current state:

- local generated-template changes make setup configure workflows without
  collecting or publishing

Risk:

- setup becomes too powerful and mixes configuration, collection, rendering,
  artifact upload, and commit behavior
- users may publish metrics before understanding privacy choices

Likely fix:

- validate setup behavior in a generated staging repository

### Dashboard Secret Entropy Override

Intended contract:

- encrypted modes fail when the dashboard secret is below the policy entropy
  threshold unless `allow-weak-dashboard-secret` is true
- the override bypasses only the entropy gate, not required secret presence,
  decryptability, encryptability, or rotation correctness

Current state:

- local action and setup workflow changes include the override

Risk:

- users may accidentally use weak human-chosen secrets, or the product may block
  advanced users who intentionally accept the risk

Likely fix:

- validate the default failure path and explicit override path in staging

### Publish Mode

Intended contract:

- `publish` is a distinct mode
- collection and publication have clear internal boundaries
- collect can run in store-only mode without committing README or Pages output

Current state:

- local action changes split collect and publish
- local template changes make `publish.yml` a separate workflow triggered by
  successful collect completion and manual dispatch

Risk:

- users who only want retained artifacts may find publication semantics hard to
  reason about
- rendering improvements are harder to describe as a separate update channel

Likely fix:

- validate artifact handoff from collect to workflow-run-triggered publish in
  staging

### Existing User Update Path

Intended contract:

- action-owned rendering transmits most UI/runtime fixes through action refs
- template changes need a separate migration story
- generated template should not ship renderer internals

Current state:

- no explicit upgrade mechanism exists

Risk:

- workflow changes may strand early users unless documented carefully

Likely fix:

- keep workflows thin
- document manual workflow migration steps
- consider future `upgrade` mode or template-sync action

### Umbrella Product Surface

Intended contract:

- `reponomics` acts as the public product home
- `reponomics-dashboard` remains the install/template artifact

Current state:

- no umbrella repo is populated

Risk:

- users may encounter the generated template first and treat it as the whole
  product, even though it is intentionally sparse

Likely fix:

- create/populate an umbrella repo once the core integration has a credible
  story, or sooner if project discoverability becomes a blocker

## Suggested Next Work Order

1. Commit and push the local `reponomics-action` contract changes.
2. Commit and push the local `reponomics-dashboard-dev` workflow/template
   changes.
3. Regenerate and publish `reponomics-dashboard`.
4. Create a private staging repository from the template.
5. Validate setup, collect, artifact restore, publish/disclosure behavior, and
   rotate-key.
6. Decide the `reponomics-dashboard-demo` model from staging evidence.
7. Create/populate the umbrella `reponomics` product repo before public launch.
