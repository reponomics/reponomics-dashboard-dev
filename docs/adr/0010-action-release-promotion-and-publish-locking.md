# ADR 0010: Action Release Promotion And Publish Locking

- Status: Accepted
- Date: 2026-05-31
- Amends: [ADR 0003](0003-generated-template-and-demo-repositories.md), [ADR 0004](0004-action-owned-upgrades-and-release-notices.md), [ADR 0005](0005-template-release-publication-policy.md)
- Complements: [ADR 0006](0006-template-repository-testing-strategy.md)

## Context

Reponomics now uses three separate release surfaces:

- `reponomics-dashboard-action` owns runtime behavior, including collection,
  retained artifact restore, schema migration, rendering, managed docs sync,
  and generated output publication behavior.
- `reponomics-dashboard-dev` owns the generated template source, release
  policy, tests, and the accepted action release used by generated workflows.
- `reponomics-dashboard` is the generated template repository that users copy.

This split is deliberate, but it creates a promotion problem. A newly published
action release is not automatically accepted by the generated template. The dev
repo must first validate that the release has the contract expected by the
template, then produce a reviewed PR that updates generated workflow refs,
docs, tests, and provenance fields consistently.

The addition of action-managed `docs-sync` sharpened the boundary. The template
must run docs sync at a point where generated docs describe the behavior used by
collection. Running docs sync during publication would allow a publish run to
render newer docs or behavior assumptions than the data was collected with.

There is a related publish concern. If collection and publication are split
across workflows, publication must not silently switch to a newer action
release or a newer `dashboard-data` artifact that appeared after the triggering
collection run. Otherwise a publish job could render data with a different
runtime model than the one that collected it.

## Decision

Use `reponomics-dashboard-dev` as the single source of truth for the accepted
`reponomics-dashboard-action` release.

The accepted release is recorded in `template-action-release.yml` with:

- action repository
- exact SemVer tag
- resolved target commit SHA
- release URL
- publication timestamp

Generated workflow refs remain exact SemVer tags for readability. The resolved
SHA is stored beside them for validation, provenance, and exact checkout during
publication.

After `reponomics-dashboard-action` publishes a release, its release workflow
uses the installed Repository Dashboard GitHub App to send a
`repository_dispatch` event to `reponomics-dashboard-dev`. The dev repo
re-fetches the release from GitHub, validates the dispatch payload against the
release, verifies the release action metadata contains the required docs-sync
contract, rewrites managed references from `template-action-release.yml`, and
opens a reviewed PR.

Merging that dev PR accepts the action release for future generated template
publication. The generated template repository is still updated only through a
`reponomics-dashboard-dev` release and the existing template publication
workflow.

## Docs Sync Placement

Generated `collect.yml` runs docs sync before collection:

1. checkout the repository
2. run `reponomics-dashboard-action` with `mode: docs-sync`
3. allow `config.yaml` to control `allow_docs_sync`, defaulting to enabled
4. run collection after docs sync completes
5. record collect provenance for any later publication

Generated `publish.yml` does not run docs sync.

This keeps managed docs and collected data in the same behavioral epoch. If an
action release changes documented behavior, the next collection run is the
point at which managed docs and collected data advance together.

Setup does not run docs sync as a separate write. Setup enables workflows and
documents that managed docs sync runs on the next collection unless
`allow_docs_sync: false` is set in `config.yaml`.

## Publish Locking

Automatic publication is locked to the triggering collection run.

Collection writes a provenance artifact containing:

- source repository and source commit SHA
- collect workflow run ID and attempt
- action repository, exact tag, and resolved action SHA
- privacy mode, retention period, and README publication setting

Publication downloads provenance and `dashboard-data` from the triggering
collect run, checks out the recorded source revision, checks out the action at
the recorded action SHA, and renders with that local action checkout.

If README publication is enabled, publish checks out `main` and verifies that
`main` still equals the recorded source SHA before committing README output. If
`main` moved after collection, publication stops and asks for a fresh
collection run. This avoids committing old generated README output on top of a
newer branch tip.

The publish workflow uses a stable concurrency group with
`cancel-in-progress: true`. If multiple collect runs complete close together,
the newest publish run wins. An older publish can be canceled by a newer one,
and if an older publish finishes first, the newer publish should overwrite it
afterward.

Manual publication remains an operator action. It uses the currently accepted
action release and the latest restorable retained artifact, because there is no
triggering collect run to lock to.

## Cross-Repo Promotion Flow

The normal flow is:

1. `reponomics-dashboard-action` merges runtime changes.
2. Release Please publishes an action release and moves floating tags.
3. The action release workflow dispatches
   `reponomics-dashboard-dev` with `{ tag, target_commitish, release_url }`.
4. `reponomics-dashboard-dev` validates the release and opens
   `automation/reponomics-dashboard-action-vX.Y.Z`.
5. Maintainers review and merge the dashboard-dev action release PR.
6. Release Please publishes a dashboard-dev release.
7. The dashboard-dev template publication workflow publishes the generated
   template repository from that release.

The action repository does not push directly to the generated template
repository. The dev repository remains the acceptance gate.

## Operational Edge Cases

### Action release before the dev receiver exists

If an action release is cut before the dev dispatch receiver is merged, no
automatic dev PR will be opened. This is acceptable for the transition. After
the receiver exists, maintainers can run the dev sync workflow manually for the
already-published action tag.

### Action release while a dashboard-dev PR is open

An open dashboard-dev PR is not a repository freeze.

If the open PR is unrelated to action-release acceptance, either PR can merge
first. If both touch generated workflows, release manifests, or docs generated
from the action release, rebase or rerun the sync workflow so the final PR is
based on current `main`.

If the action release requires dashboard-dev support that is still under
review, merge the dashboard-dev support PR first, then rerun or rebase the
action-release sync PR. The automation PR should be treated as an ordinary
reviewed PR, not as an unreviewable bot fast path.

### Dashboard-dev release while an action sync PR is open

A dashboard-dev release may happen while an action sync PR is open. The
generated template published by that release continues to use the currently
accepted action release in `template-action-release.yml`.

This is acceptable. The action sync PR only changes the accepted release after
it merges. A later dashboard-dev release will publish the generated template
with the newly accepted action release.

### Multiple action releases before dev acceptance

If two action releases are published before the first sync PR merges,
maintainers should usually accept only the latest release and close or supersede
the older PR.

The latest action release contains the previous action code history, but it may
not contain dashboard-dev support work. If a release requires new dev-side
template logic, merge that support first and rerun sync for the latest action
tag.

### Dispatch succeeds but validation fails

The dev sync workflow must fail rather than open a PR when:

- the tag is not an exact SemVer release tag
- the release URL or target commit does not match the dispatch payload
- the resolved target is not a commit SHA
- the action metadata lacks docs-sync mode documentation
- the action metadata lacks `allow-docs-sync`
- the action metadata lacks docs-sync outputs required by dashboard-dev

This protects the generated template from accepting an action release whose
contract does not match the template.

### Dashboard-data drift between collect and publish

The retained artifact name is stable and may be overwritten by later collection
runs. Automatic publish must therefore download `dashboard-data` from the
triggering collect workflow run, not from "latest" repository artifacts.

If a user or schedule triggers another collection before the first publication
finishes, two publish runs may exist. The publish concurrency policy ensures
that the newer publish wins as the final repository state.

### Action version bump between collect and publish

Automatic publish uses the action SHA recorded by collection. A dev-side action
release bump that lands between collection and publication does not affect the
in-flight publish run.

The new action release affects future generated templates and future collection
runs after the dev release and template publication flow complete.

### Managed docs write fails

Docs sync is advisory when repository permissions are missing. It should report
the inability to push managed docs without changing the collection data model.

When docs sync is disabled with `allow_docs_sync: false`, collection continues
without updating `docs/reponomics/`.

### Generated template repository is private

The generated template repository may remain private during staging. That does
not change the promotion model as long as the dashboard-dev publication token
or GitHub App installation is authorized for the template repository with the
needed contents permission.

## Rationale

This model keeps the thin-template contract and the supply-chain story aligned.
The runtime action can release independently, but dashboard-dev decides when a
specific action release is accepted into generated workflows.

Exact SemVer refs keep generated workflows readable for users. The manifest's
resolved SHA gives maintainers a precise validation and provenance target
without making every generated workflow visually hostile.

Running docs sync only before collection prevents docs, collected data, and
rendered outputs from crossing behavioral epochs. Locking publish to the
triggering collect run prevents artifact and action-version drift when schedule
runs, manual runs, or release automation overlap.

Treating automation PRs as normal reviewed PRs keeps dashboard-dev work
unblocked. The correct invariant is not "no other PR may merge while an action
sync PR is open"; the invariant is "the merged state of dashboard-dev has one
reviewed, validated accepted action release."

## Consequences

- `template-action-release.yml` becomes part of the template product contract.
- Dashboard-dev CI must verify action-release refs and action metadata.
- Action releases can create dashboard-dev PRs, but cannot bypass dev review.
- Template publication remains release-driven from dashboard-dev, so accepting
  an action release does not update the generated template until a dev release
  is published.
- Maintainers need to close or supersede stale action sync PRs when newer
  action releases are accepted first.
- Publication failures caused by `main` moving after collection are expected
  safety stops, not infrastructure failures. The remedy is to collect again.

## Non-Goals

This ADR does not:

- require generated user repositories to receive automatic PRs
- require full SHA refs in generated workflows by default
- make action releases publish directly to the generated template repository
- define final public visibility for the generated template repository
- replace Release Please as the release mechanism
- define branch protection or environment approval details for the GitHub App

