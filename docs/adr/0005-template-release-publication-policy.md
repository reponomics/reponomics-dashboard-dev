# ADR 0005: Template Release Publication Policy

- Status: Accepted
- Date: 2026-05-24

## Context

Reponomics now has a deliberate split:

- `reponomics-dashboard-action` is the runtime behavior and compatibility
  channel.
- `reponomics-dashboard` is a thin generated onboarding template.
- `reponomics-dashboard-dev` is the editable source and release automation
  surface.

Existing user repositories primarily consume behavior updates through the action
ref they pin in workflows. Template repository updates mostly affect new
repositories created after a template publish.

That means a dashboard-dev release can be operationally meaningful while
producing no change in generated template files. This raises a policy question:
should template publication be skipped when generated content is unchanged, or
should publication remain release-driven even for no-diff outputs?

## Decision

Use release-driven publication for the generated template repository.

1. A published release in `reponomics-dashboard-dev` triggers template
   publication from that release source.
2. Template publication is not diff-gated; no-diff publishes are acceptable.
3. Version lineage between `reponomics-dashboard-dev` and
   `reponomics-dashboard` is intentionally lockstep at release time.
4. Runtime compatibility policy is anchored to
   `reponomics-dashboard-action` versions, not template tags.

## Rationale

- The runtime action is the stable contract that existing repositories rely on.
- The template is intentionally thin, and keeping publication strictly
  release-driven avoids extra state and conditional behavior in release
  automation.
- No-diff template releases are low risk and low cost relative to the
  complexity of maintaining parallel "released-but-not-published" cases.
- Deterministic release-to-publication mapping is easier to audit than
  content-diff exceptions.

## Consequences

- Some template releases may not change generated file contents.
- Template release activity should not be interpreted as a direct signal of
  runtime behavior changes.
- Maintainer guidance should continue to treat action releases as the primary
  compatibility and migration signal.
- Commit discipline still matters: `feat`/`fix`/`deps` should be used when a
  release is intended, while non-releasable change types remain available for
  maintainer-only work.

## Alternatives Considered

### 1) Diff-gated template publication

Pros:
- Fewer no-op publishes.

Cons:
- Introduces additional release-state branching.
- Breaks simple one-release/one-publication reasoning.
- Adds operational edge cases without meaningful user-facing benefit.

### 2) Path-gated or fully manual release discipline only

Pros:
- Can reduce accidental releases for maintainer-only changes.

Cons:
- Still requires human interpretation of what should bump versions.
- Does not replace the need for a clear publication policy once a release is
  cut.

## Non-Goals

This ADR does not redefine:

- the runtime action compatibility contract
- semantic versioning rules for `reponomics-dashboard-action`
- user migration guidance for existing repositories

Those remain governed by action-focused policy and release notes.
