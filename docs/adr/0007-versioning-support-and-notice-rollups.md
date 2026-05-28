# ADR 0007: Versioning Clarifications, Support Policy, And Notice Rollups

- Status: Proposed
- Date: 2026-05-24
- Amends: [ADR 0004](0004-action-owned-upgrades-and-release-notices.md)

## Context

ADR 0004 established action-owned upgrades and release notices, but several
practical questions remain open:

- users may skip multiple releases before checking the dashboard
- a single latest-version notice can hide intermediate workflow/permission
  implications across a skipped range
- canonical CSV export is now a first-class user surface, so schema migration
  language needs a strict compatibility boundary
- privacy/security fixes should not force users to adopt unrelated breaking
  major-version changes
- PAT guidance should acknowledge both security posture and operational
  friction (classic vs fine-grained)

This addendum narrows those ambiguities with explicit policy.

## Decision

### 1) Notification Model: Range Rollup, Not Dashboard Changelog

Keep structured release metadata for machine checks, but render only a compact
alert in README/HTML outputs.

When the running action is behind, render one rollup notice:

- current runtime version/ref
- latest compatible target
- release count behind (`N`)
- latest release publish date
- aggregated impact flags across all skipped releases:
  - requires workflow edits
  - requires token permission changes
  - requires new secrets
  - requires manual migration
- links to:
  - latest release notes
  - compare/range view

Example:

> Update available: `v1.4.2 -> v1.9.0` (5 releases behind, published 2026-05-24).
> Review release notes.

Expected behavior for a user who skipped many releases is one concise rollup
notice plus links, not multiple in-dashboard notices.

### 2) Metadata Location: Strict Input, Narrow Output

Structured release metadata remains required, but it is an input contract for
the action, not presentation content for the dashboard body.

Either is acceptable:

- validated metadata block in release notes (existing approach), or
- validated machine-readable release asset/index.

In both cases, dashboards render fixed UI text only and must not inject remote
Markdown into output.

### 3) Compatibility Boundary: Internal Artifact Schema vs CSV Contract

"Automatic artifact schema migration" applies to retained artifact internals.
It does not permit silent breaking changes to canonical CSV export.

Within a stable major version:

- allowed: additive files/columns, additive metadata, internal migrations
- not allowed: removing/renaming canonical CSV headers, changing existing
  field semantics, changing units without compatibility shims

Any canonical CSV contract break requires:

- a new major version, or
- explicit compatibility window (dual-field/dual-format period) with
  deprecation guidance.

### 4) Semantic Versioning Trigger Matrix

| Change type | Version impact | Notes |
| --- | --- | --- |
| bug fix with no contract/permission expansion | patch | includes privacy/security bug fixes |
| additive metric using existing permissions and stable semantics | minor | must tolerate missing historical data |
| additive optional input defaulting to prior behavior | minor | required-input additions are breaking |
| internal artifact migration with unchanged canonical CSV contract | minor or patch | choose minor when user-visible behavior expands |
| broader required token permissions | major | breaking for existing tokens |
| new required secret in an existing mode | major | breaking for existing automation |
| canonical CSV rename/removal/semantic reinterpretation | major | public data contract break |
| changed privacy-mode meaning/defaults | major | disclosure boundary changes |
| output path/layout break without shims | major | downstream integration break |

### 5) Security/Privacy Backport Policy

For stable major lines (`v1+`):

- current major: full support
- previous major: security/privacy and critical reliability fixes
- older majors: end-of-life unless explicitly extended

Security/privacy fixes should be shipped as patch releases on all supported
major lines where feasible. Users must not be forced to adopt a new major
version solely to receive a security/privacy fix unless no safe backport exists.

If a safe backport is not possible:

- publish mitigation guidance for the affected major
- publish an end-of-support date
- document the fixed version line clearly

### 6) Permission Surface Planning Map

Current and likely near-term surfaces:

| Surface | API family | Fine-grained permission posture | Versioning implication if required permission broadens |
| --- | --- | --- | --- |
| traffic views/clones/referrers/paths | repository traffic endpoints | `Administration` (repo) read | major |
| stars/forks/watchers/subscribers counters | repository metadata (`GET /repos/{owner}/{repo}`) | `Metadata` (repo) read | major if new required permission |
| release notice checks | releases endpoints | public: unauthenticated allowed; private: `Contents` (repo) read | major if new required permission for private flows |
| manual Pages source selection | repository settings UI | no PAT permission required | major if replaced by required token-based automation |
| optional issue/PR advisory automation | issues / pull requests endpoints | additional write permissions | keep optional; major if required |
| optional commit status signaling | commit statuses endpoints | `Commit statuses` write | keep optional; major if required |

Planning rule:

- permission-expanding features should ship as optional capability flags first
  whenever possible
- moving optional permission requirements into the default required path is a
  breaking change

### 7) Token Guidance (Classic vs Fine-Grained PAT)

Default guidance should remain security-first while acknowledging operational
reality:

- prefer fine-grained PAT when tracking repositories under one owner with a
  bounded set of repositories and permissions
- allow classic PAT (`repo` scope) as an operational fallback for broad
  multi-repository tracking where fine-grained constraints introduce excessive
  friction
- keep Pages and Administration write permissions out of the collection token; hosted dashboard repositories should use manual Pages source selection instead
- do not prescribe a single fixed expiration policy in-repo; defer to user/org
  governance and risk posture

Notes:

- fine-grained PATs are owner-scoped and can be repository-scoped
- organization policy may require fine-grained PAT approval or block classic
  PAT usage

## Consequences

- Release notices become clearer for users who skip multiple releases.
- SemVer decisions become auditable against explicit trigger classes.
- Security/privacy maintenance burden increases due to multi-line backports.
- Compatibility risk drops for CSV consumers because rename/removal rules are
  explicit.
- Permission-expanding roadmap items can be pre-scoped before implementation.

## Alternatives Considered

### 1) Keep single latest-version notice only

Pros:
- simplest implementation

Cons:
- weak guidance for users multiple versions behind
- easy to miss intermediate required actions

### 2) Render full release notes/changelog inside dashboard

Pros:
- maximal context in one surface

Cons:
- noisy UX
- violates narrow rendering and sanitization posture
- encourages presentation-coupled metadata design

### 3) Require major upgrades for all security/privacy fixes

Pros:
- lower maintainer branch overhead

Cons:
- unacceptable risk posture for conservative users
- can force unrelated breaking adoption for urgent fixes

## Non-Goals

This addendum does not define:

- exact implementation shape of a release metadata validator
- a mandatory multi-year support timeline
- migration guides for any specific future major release
