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
- requiring new token permissions for an existing default mode
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

## Configuration Schema Updates

`config.yaml` is user-owned. The runtime reads it, setup may create or update
it during explicit setup, but normal `collect` and `publish` runs should not
silently rewrite it as an upgrade mechanism.

Compatible config schema changes should follow this model:

- missing optional keys use runtime defaults
- explicit keys in `config.yaml` are treated as user intent
- normal action modes do not commit mechanical config churn
- update notices and docs explain new configurable behavior
- users copy only the snippets they want from `docs/config.example.yaml`

The generated template should ship a product-owned reference file at
`docs/config.example.yaml`. That file can evolve with template releases and
show the current recommended config shape. It is not the active runtime config.

This gives existing users a stable path:

1. upgrade the action ref to receive fixes and compatible features
2. keep existing `config.yaml` working through runtime defaults
3. opt in or opt out of new optional behavior by copying a documented snippet
   into `config.yaml`

Privacy-sensitive features should not infer consent from a missing key. They
should default off or require explicit setup/configuration plus compatible
privacy modes.

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
- compatibility fixtures pass for supported prior config and artifact shapes
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

## Compatibility Test Policy

The action repository should carry explicit compatibility fixtures for the
supported upgrade window of the current major version. These fixtures should
model repositories created on earlier compatible versions and then run through
the current action code.

At minimum, CI should cover:

- an old `config.yaml` that omits newly introduced optional keys
- an old retained artifact manifest and CSV set
- collect after restoring old retained state
- publish after restoring old retained state
- rotate-key after restoring old encrypted retained state, when encryption
  behavior is in scope

The expected behavior is:

- old configs continue to parse
- missing optional config keys resolve through runtime defaults
- explicit old config choices continue to win
- retained artifacts migrate automatically when the change is compatible
- publish renders gracefully when historical data does not contain a newly
  introduced metric
- no normal action mode silently rewrites `config.yaml`

Compatibility fixtures should be small, deterministic, and checked into the
action repository. They should include both the artifact data and the config
shape being preserved. When a future release intentionally drops support for a
fixture, that should be treated as a breaking change or documented major-version
migration.

## Provisional Major-Version Policy

A stable major action line is a compatibility promise for the normal user path,
not a permanent promise to support every historical pre-release or every
possible artifact shape forever.

Within a major version, Reponomics should preserve:

- documented action inputs and modes
- documented config keys and their meanings
- documented privacy/disclosure semantics
- retained artifact readability through compatible migrations
- generated README and Pages output paths
- normal setup, collect, publish, and rotate-key workflows for repositories
  created on that major line

The project may cut a new major version when the product needs to:

- drop migration support for old retained artifact schemas
- remove or rename config keys, action inputs, modes, or output files
- require broader token scopes or additional secrets for default operation
- change privacy defaults or disclosure semantics
- change how encrypted/plain/disabled modes behave
- replace the generated workflow contract in a way existing repositories must
  copy deliberately
- remove compatibility shims that have become a material maintenance burden
- alter the canonical data model in a way that cannot be migrated safely during
  normal restore paths

Major upgrades should be deliberate. A user pinned to `@v1` should continue to
receive compatible `v1` fixes while `v1` is supported. They should not receive
`v2` behavior unless they edit their workflow ref to `@v2` or an exact `v2.x.y`
release.

The provisional support stance is:

- maintain the current stable major line for compatible fixes and security or
  correctness issues while it is the recommended line
- after a new major line becomes recommended, keep the prior major line on a
  limited maintenance path for critical fixes when practical
- do not promise indefinite feature backports to older majors
- document any end-of-maintenance date before advancing users toward a new
  default major line

Major release notes should include:

- what compatibility guarantee is ending
- what workflow, config, secret, or permission changes are required
- whether retained artifacts migrate automatically or require a one-time
  migration step
- whether users should preserve/download old artifacts before upgrading
- how to roll back the action ref if validation fails
