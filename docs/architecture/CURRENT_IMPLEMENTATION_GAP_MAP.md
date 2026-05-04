# Reponomics Current Implementation Gap Map

Version: 1.0 snapshot against intended design

This document describes the current implementation state so it can be compared
against the intended architecture. Unlike the other architecture documents, this
file is intentionally implementation-specific.

## Current Repository State

`reponomics-action`:

- has an initial composite action on `main`
- supports `mode: collect` and `mode: rotate-key`
- does not yet support the intended `publish` mode
- contains copied Python runtime scripts
- has local fixture tests
- currently uses `github-token` as an overloaded input for traffic API and
  artifact/repository operations
- currently uses `pages-dashboard: public` in implementation rather than the
  intended `plain` terminology
- currently uses `readme-dashboard: metrics_summary` terminology rather than
  the intended richer `enabled` README dashboard terminology
- does not yet expose the intended `allow-weak-dashboard-secret` entropy-gate
  override

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

- `github-token` is overloaded.

Risk:

- users and maintainers may misunderstand which permissions are needed and why.

Likely fix:

- split action inputs before broad testing:
  - `traffic-token`
  - `github-token`
- keep environment fallbacks for `TRAFFIC_TOKEN`, `GITHUB_TOKEN`, and `GH_TOKEN`
  with clear precedence.

### Dashboard Disclosure Naming

Intended contract:

- use `plain` to mean unencrypted dashboard output
- reserve `public` for repository visibility or public product release

Current state:

- implementation uses `pages-dashboard: public`

Risk:

- users may confuse repository visibility with dashboard encryption state.

Likely fix:

- migrate input value from `public` to `plain`
- support `public` as a deprecated alias only if needed during pre-release
  testing

### Setup Workflow Scope

Intended contract:

- setup validates selected modes and enables collection and publication
  workflows
- setup should not own collection semantics
- setup stops before first collection, after validating secrets and explaining
  the next action

Current state:

- setup calls the action in collect mode for the first run

Risk:

- setup becomes too powerful and mixes configuration, collection, rendering,
  artifact upload, and commit behavior
- users may publish metrics before understanding privacy choices

Likely fix:

- remove first collection from setup
- add clearer validation and warning summary output
- ask the user to run the collection workflow manually for the first run

### Dashboard Secret Entropy Override

Intended contract:

- encrypted modes fail when the dashboard secret is below the policy entropy
  threshold unless `allow-weak-dashboard-secret` is true
- the override bypasses only the entropy gate, not required secret presence,
  decryptability, encryptability, or rotation correctness

Current state:

- no explicit weak-secret override exists

Risk:

- users may accidentally use weak human-chosen secrets, or the product may block
  advanced users who intentionally accept the risk

Likely fix:

- add `allow-weak-dashboard-secret`, default `false`
- emit a high-visibility warning whenever the override is used

### Publish Mode

Intended contract:

- `publish` is a distinct mode
- collection and publication have clear internal boundaries
- collect can run in store-only mode without committing README or Pages output

Current state:

- collect also renders and publishes selected outputs

Risk:

- users who only want retained artifacts may find publication semantics hard to
  reason about
- rendering improvements are harder to describe as a separate update channel

Likely fix:

- add `mode: publish` before public release
- update template workflows to run `collect`, then `publish` only when
  publication is selected

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

1. Align action contract terminology and token inputs.
2. Make setup validation non-publishing and keep runtime gates inside collect,
   publish, and rotate-key.
3. Add action `publish` mode and split collect from rendering.
4. Update generated template workflows for setup, collect, publish, and rotate.
5. Regenerate and publish `reponomics-dashboard`.
6. Create a private staging repository from the template.
7. Validate setup, collect, artifact restore, publish/disclosure behavior, and
   rotate-key.
8. Decide the `reponomics-dashboard-demo` model from staging evidence.
9. Create/populate the umbrella `reponomics` product repo before public launch.
