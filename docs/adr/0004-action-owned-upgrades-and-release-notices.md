# ADR 0004: Action-Owned Upgrades And Release Notices

- Status: Accepted
- Date: 2026-05-16

## Context

Reponomics is moving toward a thin generated template plus a versioned runtime
action. The template repository should remain a low-friction onboarding shell,
while `reponomics-action` owns collection, schema handling, artifact
restore/upload, rendering, encryption, and key rotation.

That boundary creates the right mechanism for feature growth, but it also
creates a user-communication problem after launch:

- users on a moving major ref such as `reponomics/reponomics-action@v1` should
  receive compatible improvements automatically
- cautious users may pin an exact release tag or commit SHA
- pinned users still need to learn that a newer compatible release exists
  before they can choose to upgrade
- new schema-backed metrics, such as repository stars, subscribers, forks, and
  growth insights, should become available without asking users to copy runtime
  files out of a newer template repository

The product also needs a clear schema-upgrade protocol. Normal users should not
need to run a separate maintenance command for compatible additive changes, but
the action must be explicit about what kinds of changes can ship inside a major
version and what kinds require a new major version or manual migration notes.

## Decision

Treat the runtime action as the primary compatible upgrade channel.

Within a stable major version, the action may ship:

- additive canonical CSV files
- additive CSV columns
- automatic schema migrations
- new dashboard and README widgets derived from existing or newly collected
  canonical data
- new metrics available through the existing token permission model
- renderer changes that tolerate missing historical data

The action must run schema checks and compatible migrations as part of its
normal artifact restore path. A separate public `schema-update` mode is not a
v1 requirement. On `collect`, `publish`, and `rotate-key`, the action should:

1. restore the retained artifact
2. read `manifest.json`
3. compare the artifact schema to the runtime schema
4. run any needed compatible migrations
5. write updated CSV headers, files, and manifest metadata
6. continue the requested mode

New metrics are collected prospectively unless GitHub provides historical data.
For example, if a release adds `subscribers_count`, existing repositories will
start collecting it on the next upgraded collection run. Historical deltas and
charts appear only after enough post-upgrade samples exist.

Use GitHub Releases as the canonical update-notice feed. Tags are not enough,
because the tags API exposes the tag name and target commit but not curated
release notes. Releases expose a stable public API surface with release tags,
names, bodies, publication timestamps, prerelease/draft state, release URLs,
and assets.

Each public release should include a constrained machine-readable notice block
inside the release body:

```markdown
<!-- reponomics-update
{
  "headline": "Repository growth metrics",
  "summary": "Adds stars, subscribers, forks, and growth conversion insights.",
  "compatibility": "compatible",
  "migration": "automatic_after_next_collect",
  "requires_workflow_change": false,
  "requires_new_token_permissions": false
}
-->
```

The release workflow should validate this block before publishing a release.
The runtime action may then query GitHub Releases during `publish`, extract only
the validated notice metadata, and render a small update notice when a newer
compatible release exists.

The rendered notice should be deliberately narrow. It may include:

- latest release tag
- headline
- short summary
- compatibility category
- migration expectation
- whether workflow or token changes are required
- a link to the GitHub release

It must not render arbitrary remote Markdown directly into README or Pages
outputs.

## User Upgrade Postures

Reponomics supports three normal upgrade postures:

| Action ref | Behavior |
|------------|----------|
| `@v1` | Receives compatible v1 runtime, schema, and dashboard improvements automatically. |
| exact release tag or SHA | Runtime behavior is frozen until the user edits workflow refs. Update notices may still be displayed by the pinned code if that code supports release checks. |
| forked action | Fully self-managed; Reponomics release notices may not apply. |

Normal users on `@v1` should not need to do anything for compatible upgrades.
After the next scheduled or manual collection run, new fields begin collecting.
After publish runs, README and Pages outputs render whatever the retained data
can support.

Pinned users should:

1. read the update notice or release notes
2. edit their workflow action refs to the desired release
3. run collection once
4. run publication if it does not happen automatically
5. optionally pin back to an exact tag or SHA after validation

## Breaking Changes

The following changes require a new major version or explicit migration notes:

- changed privacy defaults
- removed fields, files, modes, inputs, or supported artifact layouts
- new required secrets
- broader required token permissions
- changed meanings of existing fields
- committed output path changes without compatibility shims
- migrations that cannot run safely inside the normal restore path

## Rationale

This keeps the template-first product model intact. Existing users should get
compatible feature work by upgrading the action ref, not by copying runtime
scripts, renderer templates, or schema files from a newer template repository.

It also respects supply-chain caution. A user who pins an exact action version
does not run newer Reponomics code. The pinned action may only fetch and render
sanitized release metadata so the user knows an upgrade exists.

GitHub Releases are a better notice source than a separate JSON feed because
they are already part of the release cycle. Maintainers should not have to
remember an additional publication ritual after cutting an action release. A
validated release-note block gives the dashboard structured metadata while
keeping GitHub's release page as the human-readable source of truth.

## Consequences

- Release discipline becomes part of the product contract. Release notes need
  a validated Reponomics notice block before publication.
- Runtime code needs a best-effort release-check client that never fails
  collection or publication when GitHub's release API is unavailable.
- Renderers need a small update-notice surface in README and HTML outputs.
- The action should record enough runtime identity to compare the running
  version/ref with published releases. For composite actions, `github.action_ref`
  and `github.action_repository` should be passed through environment variables
  by the workflow/action metadata rather than referenced directly in shell
  commands.
- Compatible migrations must be tested as first-class runtime behavior, not
  treated as documentation-only instructions.
- New metrics may have partial historical coverage. Dashboards must present
  "available since first collected" behavior gracefully.

## Security And Reliability Boundaries

Update notices are metadata, not code.

The action must not:

- fetch and execute remote release assets
- inject arbitrary release Markdown into generated outputs
- fail the main collection or publish path solely because release checking
  failed
- leak secrets or token values in update diagnostics
- automatically modify the user's workflow action ref

The action may:

- call the public GitHub Releases API for `reponomics/reponomics-action`
- use the caller's existing GitHub token only if needed for rate limits
- omit update notices when the release check fails
- expose an opt-out setting for users who do not want network update checks

## Non-Goals

This ADR does not require:

- a separate public `schema-update` action mode for v1
- automatic pull requests to bump user workflow refs
- a standalone changelog service or custom feed
- rendering full release notes inside the generated dashboard
- backfilling historical values for metrics GitHub only exposes as current
  counters

