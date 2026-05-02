# Reponomics Versioning And Update Policy

Version: 0.1 intended design

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

Template shell updates require a separate mechanism.

Possible mechanisms:

1. documentation-only manual migration steps
2. an `upgrade` mode in `reponomics-action`
3. a separate template sync action
4. a release note that tells users exactly which workflow/doc changes to copy

Preferred direction:

- Runtime rendering and storage behavior should live in `reponomics-action` so
  most users do not need to pull template changes for UI improvements.
- Template-owned files should be limited to workflows, docs, config defaults,
  and placeholders.
- Workflow changes should be rare, explicit, and migration-documented.

## Dashboard Templates And Rendering Ownership

The dashboard renderer should be action-owned if it needs to update existing
users. If dashboard templates live only in `reponomics-dashboard`, then users
who already created repositories will not get renderer fixes or new UI without
copying template files.

Therefore:

- runtime renderers should live in `reponomics-action`
- generated `reponomics-dashboard` should ship placeholders and workflow
  shells, not renderer templates
- if user-customizable dashboard templates are introduced, they should be
  versioned build artifacts with explicit compatibility rules

Possible future model:

- `reponomics-action` publishes renderer bundles by version
- user workflows reference a renderer version or action version
- advanced users can override templates locally
- the action reports when local overrides are older than the runtime contract

## Release Gates

Before advancing a stable action tag:

- action tests pass
- fixture collect passes
- fixture rotate-key passes
- staging consumer collect passes
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

