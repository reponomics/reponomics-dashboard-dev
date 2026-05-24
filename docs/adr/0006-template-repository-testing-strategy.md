# ADR 0006: Template Repository Testing Strategy

- Status: Proposed
- Date: 2026-05-24

## Context

`reponomics-dashboard-dev` ships a generated template repository to
`reponomics-dashboard`. The highest operational risk is not only Python script
correctness, but also whether generated template workflows remain runnable in
real GitHub repository conditions (permissions, Pages setup, workflow dispatch,
and secret expectations).

We need strong confidence before and during pre-release public hardening, but
we do not want to build and maintain a large end-to-end suite all at once.

## Decision

Adopt a phased three-layer strategy for testing the template repository.

### Layer 1: Deterministic contract and quality checks (required on PRs)

Keep fast, deterministic checks as required branch gates:

- lint and typecheck for maintainer scripts
- coverage gate for maintainer scripts
- generated template contract checks (required files, forbidden files,
  workflow/action contract assertions)
- workflow classification verification
- template build dry run

These checks run without external GitHub API side effects.

### Layer 2: Ephemeral publish smoke checks (required on PRs)

Keep a required smoke check that:

1. builds `dist/template`
2. publishes to an ephemeral local bare remote
3. lints generated workflows (including disabled workflow variants) with
   `actionlint`

This validates template publication mechanics and workflow syntax while staying
deterministic in CI.

### Layer 3: Live GitHub canary checks (nightly/manual, non-blocking at first)

Add a separate canary workflow that:

1. creates a temporary GitHub repository
2. pushes generated template output
3. dispatches template workflows (`setup`, then `collect`, `publish`,
   `rotate-key`) with controlled inputs/secrets
4. verifies expected workflow outcomes and produced artifacts/pages state
5. tears down the temporary repository

Layer 3 should start as non-blocking (nightly and manual trigger), then be
re-evaluated after flake/stability data is available.

## Rollout Policy

1. Do not block pull requests on live canary checks initially.
2. Keep live canary credentials and permissions narrowly scoped to temporary
   repository management and workflow execution.
3. Keep required PR checks deterministic; avoid coupling mergeability to
   external service availability.
4. Increase coverage and strictness incrementally as the script surface grows.

## Rationale

- Fast required checks protect day-to-day developer flow.
- Smoke publication catches template packaging and workflow-syntax regressions.
- A separate live canary is the only reliable way to validate GitHub-native
  behavior (workflow dispatch, Pages, token/permission edges) without making
  every PR depend on live platform conditions.

This split gives early confidence now while keeping maintenance cost controlled.

## Consequences

- Some failures will surface in canary runs rather than PR checks.
- Maintainers must monitor canary results and treat repeated failures as release
  blockers for template publication.
- Additional operational automation is needed for safe temporary-repository
  lifecycle management.

## Alternatives Considered

### 1) Full live end-to-end checks on every PR

Pros:
- Highest realism for every change.

Cons:
- Higher flake rate and slower feedback.
- Mergeability depends on external GitHub API/runtime conditions.

### 2) Deterministic/unit checks only

Pros:
- Fastest and simplest CI.

Cons:
- Misses real-world workflow integration failures until late.

### 3) Build all phases immediately

Pros:
- Faster path to maximal test surface.

Cons:
- Higher implementation and maintenance overhead during active architecture
  changes.

## Non-Goals

This ADR does not define:

- v1 feature-completeness requirements
- public launch marketing readiness
- post-public paid security-feature configuration (for example private-repo
  pricing-gated toggles)

## Implementation Status, 2026-05-24

Layers 1 and 2 are already in place through current `DEV / CI`,
`tests/test_generated_repos.py`, `make verify`, and
`scripts/smoke_template_release.py`.

Layer 3 (live canary repository workflow) is intentionally deferred and should
be implemented in a follow-up change set.
