# ADR 0002: Discovery-First Tracking And Disposable Template Shell

- Status: Superseded
- Date: 2026-04-10

> Historical note: this ADR captured the first discovery-first selection model.
> The current product no longer re-ranks tracked repositories by recent
> activity. Selection now uses explicit include/exclude controls plus a stable
> automatic pool.

## Context

The original template contract required users to list tracked repositories in
`config.yaml`. That made the collector explicit, but it also created friction
in the happy path and complicated future template upgrades.

Two product realities pushed the design in a different direction:

- most users do not want to maintain a full inventory of repositories just to
  start collecting traffic
- the durable state for this product is the artifact-backed CSV history, not
  the git worktree

At the same time, the repository has begun moving toward a future "sync with
template" model where the repo contents can be refreshed aggressively while the
collected history persists separately.

## Decision

Adopt a discovery-first collection model.

The collector now:

1. discovers repositories visible to the authenticated user
2. excludes forks and archived repositories
3. keeps only repositories where the authenticated user has push access
4. sorts candidates by recent activity
5. caps the tracked set at `50`

`config.yaml` remains in the product, but only as an optional override layer.
When present:

- `repos` entries are moved to the front of the discovered set if they are
  still eligible
- `exclude_repos` entries are omitted from future tracking and hidden from the
  rendered README/dashboard, while their retained history remains in the
  artifact until trimmed by retention

The reporting surfaces remain intentionally narrow:

- the README emphasizes the most important snapshot information
- richer exploration lives in the HTML dashboard

## Rationale

This model is a better fit for the template product than the previous
configuration-first design.

- It removes a setup step from the common path.
- It matches how most small teams think about their repos: "show me my active
  ones," not "I want to curate a formal inventory."
- It keeps the dashboard usable by hard-limiting the tracked set.
- It reduces the amount of file-level user state that a future template-sync
  mechanism would need to preserve.

Most importantly, this decision supports a cleaner upgrade story. If discovery
is the default and the artifact is the durable state, the repository itself can
be treated much more like a disposable shell that renders from restored data.

## Consequences

- The product default is now opinionated. Users get automatic tracking of
  active, non-fork, non-archived repositories instead of full manual control.
- `config.yaml` no longer means "track only these repos." It now provides
  lightweight priority and exclusion overrides on top of discovery.
- API usage now includes repository discovery calls in addition to the traffic
  endpoints.
- A user with a very large accessible repo graph may see the tracked set shift
  over time as activity changes, unless they pin priorities in `config.yaml`.

## Non-Goals

This ADR does **not** yet implement:

- a full "Sync with Template" workflow
- artifact-side state snapshots for template refreshes
- schema migration logic for future force-sync upgrades
- advanced repo-selection DSLs or multiple configuration modes

Those can be layered on top later if the discovery-first model proves stable.
