# Reponomics Versioning And Update Policy

Status: current for action `v0.20.3` and pre-v1 template hardening.

Reponomics has two update channels:

1. runtime behavior through `reponomics-dashboard-action`
2. template shell changes through `reponomics-dashboard`

The action is the main update channel for existing user repositories. The generated template is the starter surface for new repositories.

## Action Versioning

Before `v1`, generated workflows should pin an explicit accepted release such as:

```yaml
uses: reponomics/reponomics-dashboard-action@v0.20.3
```

Dashboard-dev records the accepted template action release in `template-action-release.yml`. Template workflow refs, generated docs, and tests are synchronized from that single source of truth.

The generated collect workflow also embeds the accepted action tag and resolved action commit SHA as workflow environment. When publishing is enabled, collect uploads those values with the collected repository SHA in a `reponomics-collect-provenance` artifact. The separate publish workflow consumes that artifact, restores `dashboard-data` from the recorded collect workflow run, and checks out the recorded action commit as a local action before rendering, so a later collect or template action bump cannot publish an older retained artifact under a newer action/data contract.

Pre-v1 releases may change inputs, retained artifact schema, generated dashboard structure, migration behavior, or docs. Users should review release notes before changing pre-v1 refs.

After the stable contract is accepted:

- stable users can reference a moving `@v1` tag
- cautious users can pin exact `v1.x.y` tags or full commit SHAs
- breaking input or storage changes require a new major version or explicit migration guidance

## Compatible Runtime Changes

Within a stable major version, the action may add:

- compatible CSV columns or CSV files
- automatic artifact schema migrations
- new README/dashboard widgets that tolerate missing history
- renderer improvements
- release notices
- bug fixes and security hardening

The action must not silently rewrite user-owned `config.yaml` during normal collection or publication.

## Template Changes

Template changes affect new repositories and setup workflow shells. They are published by regenerating `reponomics-dashboard` from `reponomics-dashboard-dev`.

Existing users receive template-shell changes only if they manually copy them or migrate. Runtime-compatible improvements should therefore live in the action whenever possible.

## Update Notices

Action release notes may include one constrained metadata block:

```markdown
<!-- reponomics-update {"title":"Upgrade available","summary":"Compatible runtime and artifact migration update.","min_runtime_version":"0.1.0","action_refs":["v1"]} -->
```

Supported keys are:

- `title`
- `summary`
- `min_runtime_version`
- `max_runtime_version`
- `action_refs`
- `action_repository`

When present, `action_repository` must be `reponomics/reponomics-dashboard-action`. Renderers may display parsed metadata only; arbitrary release Markdown must not be injected into dashboards.

## Breaking Changes

Treat these as breaking unless compatibility shims or migrations are provided:

- removing or renaming action inputs
- changing the meaning of `strong`, `casual`, or `plain`
- changing retained artifact encryption/storage behavior
- changing the canonical artifact payload without migration
- broadening required token permissions
- adding required secrets to an existing mode
- changing where generated outputs are committed or deployed
