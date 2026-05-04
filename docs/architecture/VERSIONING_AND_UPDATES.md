# Reponomics Versioning And Update Policy

Version: 1.0 intended design

Reponomics has two update channels:

1. runtime behavior through `reponomics-action`
2. template shell changes through `reponomics-dashboard`

The action is the main update channel for existing user repositories. The
template repository is the starter surface for new repositories.

## Action Versioning

Before public release:

- workflows may reference `reponomics/reponomics-action@main`
- pre-release tags may use `v0.x.y`
- integration repos may pin exact commits when debugging

After public release:

- stable users should reference `@v1`
- exact releases should use `v1.x.y`
- the moving `v1` tag should advance only to backwards-compatible releases
- security or critical bug fixes may be backported to supported major versions

Breaking changes include:

- removing or renaming action inputs
- changing default privacy/disclosure behavior
- changing retained artifact format without migration
- changing required secrets
- changing committed output paths without compatibility
- changing workflow permissions required by normal operation
- changing the meaning of `plain`, `encrypted`, or `disabled`
- changing dashboard secret entropy gate semantics or removing the
  `allow-weak-dashboard-secret` override

Non-breaking changes include:

- renderer/UI improvements that preserve inputs and privacy semantics
- bug fixes
- additive action outputs
- support for new optional modes
- schema migrations that run automatically and safely

## Template Versioning

`reponomics-dashboard` is generated from `reponomics-dashboard-dev`.

The template should have:

- generated commit provenance pointing back to `reponomics-dashboard-dev`
- release notes for meaningful template changes
- a visible template version, either in docs or a small metadata file

Template changes affect new repositories automatically only when they are
created after the template is updated. Existing repositories do not receive
template file changes unless they opt into an upgrade path.

## Existing User Updates

Existing repositories receive runtime updates through their pinned action ref.

If a user pins:

- `@main`: they receive all pre-release runtime changes immediately.
- `@v1`: they receive compatible v1 runtime updates when the moving tag
  advances.
- exact tag or SHA: they receive no runtime updates until they change the ref.

Template shell updates require a separate mechanism. The v1 policy is:

- runtime rendering, storage behavior, schema migrations, and compatible UI
  improvements live in `reponomics-action`
- template-owned files are limited to workflows, docs, config defaults, and
  placeholders
- workflow changes are rare, explicit, and migration-documented
- existing users do not need to copy template files for compatible dashboard UI
  improvements
- when a workflow/config/docs change is required, release notes provide exact
  manual migration steps

A future setup validation or upgrade check can detect stale workflow shells and
print instructions, but automatic workflow mutation is not required for v1.

## Dashboard Rendering Ownership

The dashboard renderer is action-owned because it needs to update existing
users. If dashboard templates or rendering scripts live only in
`reponomics-dashboard`, then users who already created repositories will not get
renderer fixes or new UI without copying template files.

Therefore:

- runtime renderers should live in `reponomics-action`
- generated `reponomics-dashboard` should ship placeholders and workflow
  shells, not renderer templates
- action `publish` mode should render README, Pages, and asset outputs from
  retained data
- compatible renderer changes should ship through action releases

Future advanced model:

- `reponomics-action` publishes renderer bundles by version
- user workflows reference a renderer version or action version
- advanced users can override templates locally
- the action reports when local overrides are older than the runtime contract

## Release Gates

Before advancing a stable action tag:

- action tests pass
- fixture collect passes
- fixture publish passes
- fixture rotate-key passes
- staging consumer collect passes
- staging consumer publish passes
- staging consumer rotate-key passes
- privacy/disclosure behavior matches docs

Before publishing `reponomics-dashboard`:

- template generation tests pass
- generated file set is thin
- workflows reference the intended action ref
- no runtime internals are included
- setup docs and privacy docs match the action contract

## Communicating Changes

Every release should state:

- whether existing users get the change automatically through their action ref
- whether existing users must copy workflow/template changes
- whether secrets or permissions changed
- whether retained artifacts migrate automatically
- whether the change affects committed output disclosure
