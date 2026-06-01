# ADR 0008: Incident Sentinel Artifact Preservation Workflow

- Status: Proposed
- Date: 2026-05-25
- Complements: [ADR 0001](0001-encrypted-pages-mode.md), [ADR 0006](0006-template-repository-testing-strategy.md)
- Related action ADR: [ADR 005](https://github.com/reponomics/reponomics-dashboard-action/blob/main/docs/adr/005-incident-reset-rekey-and-history-purge.md)

## Context

The canonical analytics state for generated dashboard repositories is the `dashboard-data` GitHub Actions artifact, not git history. Collection is additive over time, but the current `collect` run must succeed often enough to restore the previous artifact and upload a fresh one before retention expiry.

A realistic outage class is repeated collection failure caused by token expiry, permission drift, or transient platform/API issues. If failures continue longer than artifact retention, the canonical retained history can expire even though repository workflows still exist.

`incident-reset` in the action runtime addresses a different problem: compromised encryption history that requires destructive purge and re-encryption under a new key. It is not a passive continuity mechanism for ordinary collection outages.

We need an automated, low-friction safeguard that preserves the latest unexpired canonical artifact during collection outages without changing the privacy model or requiring decryption.

## Decision

Add a dedicated template workflow: `.github/workflows/incident-sentinel.yml.disabled`.

The setup workflow enables this sentinel workflow alongside `collect` so generated repositories receive it automatically.

Sentinel behavior:

- Trigger on `workflow_run` completion for `Collect Reponomics Data` on `main` when the upstream run conclusion is `failure`.
- Allow manual `workflow_dispatch` for operator-initiated preservation checks.
- Resolve candidate source artifacts by first checking the triggering run for `dashboard-data`, then falling back to repository-level `dashboard-data` artifacts.
- Filter to non-expired artifacts and prefer the newest candidate on `main`.
- Download the selected artifact archive and re-upload it as `dashboard-data` with `retention-days: 90` and `overwrite: true`.
- Exit cleanly with an explicit summary note when no unexpired source artifact is available.

Permission model:

- Top-level workflow permissions remain `contents: read`.
- The preserve job elevates only what is required for artifact maintenance: `actions: write` plus `contents: read`.

The sentinel is intentionally a separate workflow (not folded into collect/publish) to match the repository mental model: setup, collect, publish, rotate-key, and incident response are operationally distinct concerns.

## Consequences

- Outage resilience improves because canonical history can be kept alive during repeated collection failures without manual artifact handling.
- The safeguard is format-agnostic: encrypted and plain artifacts are preserved byte-for-byte without decrypt/re-encrypt steps.
- Operators still lose history if all source artifacts are already expired before sentinel runs.
- Sentinel does not remediate compromised-history incidents; `incident-reset`
  remains required for secret exposure scenarios. In the generated template,
  `incident-reset` is exposed from the collect workflow's manual dispatch path
  so the runtime can delete prior runs and `dashboard-data` artifacts from the
  same workflow that normally creates retained dashboard history.
- Repeated upstream failures can produce additional maintenance runs, but each run is bounded and idempotent around the latest `dashboard-data` artifact name.

## Alternatives Considered

### 1) Rely on manual artifact retention extension

Pros:
- No new workflow surface.

Cons:
- High operator burden during outages.
- Easy to miss expiry windows.

### 2) Move preservation logic into the collect runtime path

Pros:
- Fewer workflow files.

Cons:
- Does not run when collect fails before persistence stages.
- Blurs normal collection behavior with incident response behavior.

### 3) Use a PAT-only sentinel path

Pros:
- Explicit token control.

Cons:
- Increases secret requirements for a resilience safeguard.
- Unnecessary for same-repo artifact operations when job-scoped `actions: write` is available.

## Non-Goals

This ADR does not define:

- automated repair of expired/revoked PATs or workflow permissions
- destructive purge semantics for leaked-history incidents
- changes to canonical CSV schema or privacy-mode behavior

## Implementation Status, 2026-05-25

Implemented in `reponomics-dashboard-dev` with template manifest and workflow classification/test contract updates.
