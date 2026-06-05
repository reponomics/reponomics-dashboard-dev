# ADR 0009: Scheduled Workflow Keepalive

- Status: Proposed
- Date: 2026-05-27
- Complements: [ADR 0008](0008-outage-sentinel-artifact-preservation.md)

## Context

The dashboard depends on scheduled GitHub Actions workflows for collection and publication. GitHub documents that scheduled workflows in public repositories may be disabled automatically after 60 days without repository activity, but it does not precisely define the activity criteria for that policy. Inactive scheduled workflows are an operational risk for dashboard repositories regardless of visibility, because artifact expiry and missed collection windows have the same product impact.

This creates a separate operational risk from collection failure. `outage-sentinel` can preserve the latest unexpired `dashboard-data` artifact when collection fails, but it cannot run if GitHub silently disables scheduled workflow triggers.

Users also need an explicit reminder that the retained artifact is the canonical data store and should be downloaded before expiry if workflow scheduling fails in a way our safeguards do not catch.

## Decision

Add a dedicated template workflow: `.github/workflows/keepalive.yml.disabled`.

The setup workflow enables this keepalive workflow alongside `collect` and `outage-sentinel` so generated repositories receive it automatically.

Keepalive behavior:

- Run monthly on `main` across repository visibility modes.
- Use only the repository `GITHUB_TOKEN`; do not use `COLLECTION_TOKEN` or dashboard secrets.
- Commit `.reponomics/keepalive.md` with the latest keepalive timestamp and an operational warning.
- Try to create one persistent reminder issue explaining the 60-day scheduled workflow risk and the need to download `dashboard-data` if workflows stop unexpectedly.
- Treat reminder issue creation as best-effort so repositories with Issues disabled still receive the marker commit and a workflow summary.

Permission model:

- Top-level workflow permissions remain `contents: read`.
- The keepalive job elevates only the permissions it needs: `contents: write` for the marker commit and `issues: write` for the persistent reminder issue.

## Consequences

- Generated repositories get regular repository activity intended to reduce the chance of silent scheduled-workflow disablement.
- Users see a durable warning in the repository issue tracker when Issues are enabled.
- The safeguard is still best-effort because GitHub does not define whether every workflow-authored activity counts for this policy.
- The workflow creates intentional commit history noise: one small keepalive commit per month in public dashboard repositories.
- The workflow does not replace outage-sentinel; keepalive is scheduler liveness, while outage-sentinel is artifact preservation during known collection outages.

## Alternatives Considered

### 1) Documentation-only warning

Pros:
- No additional workflow surface.
- No additional commits or issue permissions.

Cons:
- Too easy for users to miss.
- Does not create repository activity.

### 2) Fold keepalive into collect

Pros:
- Fewer workflow files.

Cons:
- Does not help when scheduled collection itself is disabled.
- Blurs normal collection with scheduler liveness.

### 3) Require user-managed calendar reminders

Pros:
- No automation permissions.

Cons:
- High operational burden.
- Easy to miss before artifact expiry.

## Non-Goals

This ADR does not define:

- external monitoring or notification services
- guaranteed prevention of GitHub scheduled workflow disablement
- changes to artifact retention policy
- changes to collection, publication, or key rotation semantics
