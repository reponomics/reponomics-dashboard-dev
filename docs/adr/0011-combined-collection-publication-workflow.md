# ADR 0011: Combined Collection And Publication Workflow

- Status: Proposed
- Date: 2026-06-07
- Amends: [ADR 0010](0010-action-release-promotion-and-publish-locking.md)
- Complements: [ADR 0004](0004-action-owned-upgrades-and-release-notices.md), [ADR 0006](0006-template-repository-testing-strategy.md), [ADR 0007](0007-versioning-support-and-notice-rollups.md)

## Context

The generated template currently splits collection and publication across separate workflows. `collect.yml` stores retained dashboard data and uploads a provenance artifact. `publish.yml` is triggered by `workflow_run`, downloads the provenance from the triggering collect run, verifies that provenance, checks out the recorded source revision, checks out the recorded `reponomics-dashboard-action` commit, and renders with that local action checkout.

That model protects an important invariant: publication must render retained data with the same runtime/data contract that collected it. The cost is that a large amount of orchestration logic lives in the generated template repository:

- provenance construction and upload
- provenance validation and GitHub API tag resolution
- collect-run matching
- action checkout by recorded SHA
- dashboard-data artifact selection
- special manual publication behavior

This is heavier than the desired template shape. Ideally the generated repository should remain an activation shell: it owns triggers, permissions, secret names, and user configuration, while `reponomics-dashboard-action` owns runtime behavior.

There is also an upgrade-policy concern. The default target user wants compatible fixes, rendering improvements, managed documentation updates, schema migrations, and additive collection support without manually editing workflow refs. Exact-tag and SHA-pinned consumption must remain supported, but they are more operationally demanding because the user must actively review and apply compatible runtime updates. Delayed updates are usually acceptable for metrics that Reponomics already collects completely; the stronger data-coverage concern applies to future additive collectors backed by bounded source windows, such as event streams.

During the current pre-public hardening period, breaking generated-template changes are acceptable. This is the right time to simplify the workflow topology before public users depend on the existing split model.

## Decision

Replace the default split `collect.yml` plus automatic `publish.yml` topology with a single generated `collect-and-publish.yml` workflow.

The workflow runs on the existing collection schedule and on manual dispatch. Manual dispatch includes a `skip_collect` boolean input:

- `skip_collect: false` collects fresh data and then publishes from that same run when publication is enabled.
- `skip_collect: true` republishes from the latest retained dashboard data and the last successful collect provenance without collecting fresh GitHub data.

The scheduled default path is collect plus publish. The manual republish path exists for publication-surface recovery and configuration changes, such as:

- GitHub Pages was not configured for GitHub Actions during the previous publish attempt.
- Pages deployment failed transiently.
- README publication failed because `main` moved or repository policy blocked the commit.
- The user changed dashboard presentation or publication settings and wants to re-render retained data immediately.
- A runtime release changes rendering or managed documentation behavior and the user wants to republish before the next scheduled collection.

Collection remains the authority for the data epoch. A successful collect writes durable provenance that records:

- source repository
- source commit SHA
- collect workflow run ID and attempt
- action repository
- action ref requested by the generated workflow
- resolved action commit SHA
- runtime version
- privacy mode
- retention period
- publication settings

Publication in the same workflow run may use the freshly collected artifact directly. Republish with `skip_collect: true` must use the last collect provenance and must not blindly render with whatever a floating action ref points at during the republish run.

## Default Action Ref Policy

After the stable public contract exists, generated workflows should default to the supported major line:

```yaml
uses: reponomics/reponomics-dashboard-action@v0
```

This default optimizes for ordinary users who expect compatible fixes, managed documentation updates, schema migrations, rendering improvements, and additive collection support to arrive automatically. Exact release tags and full commit SHAs remain supported for users who prefer frozen runtime behavior.

Pinned users should receive clear status notices in generated dashboard surfaces and workflow summaries. The notice should explain the consequence, not merely report version numbers: compatible fixes, rendering changes, documentation updates, and additive collection support will not run until the pinned ref is updated.

Pre-v1 hardening uses the current floating major ref for internal validation; public documentation should advance the default major when the stable contract is accepted.

## Template Boundary

The generated workflow should keep only caller-owned concerns:

- triggers
- schedule
- manual `skip_collect` input
- workflow and job permissions
- concurrency policy
- checkout of the user repository
- explicit secret and token wiring
- optional user-owned GitHub App token minting, if retained

The action side should own:

- setup marker handling
- config parsing
- privacy-mode validation
- incomplete key-rotation guardrails
- collection credential validation after token selection
- docs sync placement
- retained artifact restore and upload
- collect provenance write and upload
- publish provenance validation
- publication artifact selection
- README and Pages publication behavior
- user-facing workflow summaries

The local workflow may still need one or more jobs so permissions stay scoped. For example, the collect job should not need Pages or `id-token` permissions, while the publish job may need them when hosted dashboard publication is enabled. The file can contain multiple jobs while still being one user-facing operational workflow.

## Sketch

The generated workflow should trend toward this shape:

```yaml
name: Collect And Publish Reponomics Dashboard

on:
  schedule:
    - cron: "0 6 * * *"
    - cron: "0 18 * * *"
  workflow_dispatch:
    inputs:
      skip_collect:
        description: "Republish existing retained data without collecting"
        type: boolean
        required: true
        default: false

permissions:
  contents: read

concurrency:
  group: reponomics-collect-publish-${{ github.ref }}
  cancel-in-progress: false

jobs:
  collect:
    if: ${{ github.ref == 'refs/heads/main' && (github.event_name != 'workflow_dispatch' || !inputs.skip_collect) }}
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: write
    steps:
      - uses: actions/checkout@v6
        with:
          ref: main

      - uses: reponomics/reponomics-dashboard-action@v0
        with:
          mode: collect
          config-path: config.yaml
          collection-token: ${{ secrets.COLLECTION_TOKEN }}
          github-token: ${{ github.token }}
          dashboard-secret: ${{ secrets.DASHBOARD_SECRET_DO_NOT_REPLACE }}

  publish:
    if: ${{ github.ref == 'refs/heads/main' && (github.event_name != 'workflow_dispatch' || !inputs.skip_collect) }}
    needs: collect
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: read
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          ref: main

      - uses: reponomics/reponomics-dashboard-action@v0
        with:
          mode: publish
          config-path: config.yaml
          artifact-run-id: ${{ github.run_id }}
          github-token: ${{ github.token }}
          dashboard-secret: ${{ secrets.DASHBOARD_SECRET_DO_NOT_REPLACE }}

  republish:
    if: ${{ github.ref == 'refs/heads/main' && github.event_name == 'workflow_dispatch' && inputs.skip_collect }}
    runs-on: ubuntu-latest
    permissions:
      contents: write
      actions: read
      pages: write
      id-token: write
    steps:
      - uses: actions/checkout@v6
        with:
          ref: main

      - uses: reponomics/reponomics-dashboard-action@v0
        with:
          mode: publish
          config-path: config.yaml
          artifact-run-id: ""
          github-token: ${{ github.token }}
          dashboard-secret: ${{ secrets.DASHBOARD_SECRET_DO_NOT_REPLACE }}
```

The sketch is illustrative, not final syntax. In particular, the action may need a more explicit input than an empty `artifact-run-id` to distinguish same-run publish from latest-retained-data republish.

## Rationale

Combining collection and default publication removes the cross-workflow trigger race. The default publish job no longer has to prove that the triggering `workflow_run` matches the provenance artifact, because both jobs are part of the same workflow run.

The model also reduces workflow count and user-facing complexity. A user can run one workflow manually and choose whether to collect fresh data or republish retained data.

The `skip_collect` path preserves the useful parts of independent publication without keeping automatic publication as a separate workflow. Users can recover from Pages configuration mistakes, transient deployment failures, README commit failures, or presentation-only configuration changes without waiting for the next scheduled collection.

The action remains the correct home for provenance logic. Provenance describes runtime behavior and artifact compatibility; keeping it in generated shell workflows makes every future runtime contract change harder to ship.

Defaulting to major-version action refs after v1 is consistent with the product's normal-user posture. Users who want frozen dependencies can pin exact tags or SHAs, but they should knowingly accept the update-review burden. For already-collected metrics this is primarily a maintenance and feature-discovery tradeoff; for future bounded-window data sources it may also become a data-coverage tradeoff.

## Consequences

- The generated template workflow set can become smaller.
- Automatic `workflow_run` publication can be removed from the default path.
- The action needs new runtime/orchestration support for provenance write, provenance restore, and republish-only publication.
- Dashboard-dev tests must be updated around one combined workflow instead of separate collect and automatic publish workflows.
- Existing pre-public generated repositories may need to be regenerated or manually migrated.
- Documentation must explain `skip_collect` as republish, not as a way to bypass first setup or retained data requirements.
- Job-level permissions still require care; collapsing workflows does not mean every job should receive every permission.

## Implementation Plan

1. Add action-side provenance support for collect.
   - Record source repository, source SHA, workflow run ID, action repository, requested action ref, resolved action SHA, runtime version, privacy mode, retention, and publication settings.
   - Upload the provenance artifact after retained dashboard data is uploaded.
   - Prefer the actual action checkout SHA over a template-maintained SHA environment variable.

2. Add action-side publish provenance handling.
   - For same-run publish, support restoring the `dashboard-data` artifact from `github.run_id`.
   - For `skip_collect` republish, restore the latest retained dashboard data and its matching provenance.
   - Validate that publication uses the runtime contract recorded by collection.

3. Move template-local publish orchestration into the action.
   - Remove embedded Python provenance validation from the generated workflow.
   - Remove template-side action tag resolution.
   - Remove template-side local checkout of `reponomics-dashboard-action` where possible.
   - Keep any unavoidable local checkout only as an action-owned implementation detail or clearly documented compatibility bridge.

4. Generate `collect-and-publish.yml`.
   - Replace scheduled `collect.yml` and automatic `publish.yml`.
   - Add manual `skip_collect`.
   - Keep job permissions scoped.
   - Preserve branch gating and concurrency.

5. Keep or replace manual publish deliberately.
   - Prefer removing separate automatic publish.
   - If a separate manual-only publish workflow remains, make it a thin alias for `skip_collect` behavior or document why it exists.

6. Update setup and keepalive after the collect/publish migration.
   - Consider adding action modes for `setup` and `keepalive`.
   - Keep local manual inputs and permission envelopes in generated workflows.

7. Update dashboard-dev tests and docs.
   - Replace assertions that expect separate automatic `publish.yml`.
   - Add tests for `skip_collect` dispatch.
   - Add tests that collect provenance is action-owned.
   - Update versioning and provenance docs to describe major-ref defaults and pinned-user consequences.

8. Validate with template-consumer scenarios.
   - Fresh setup, collect, publish.
   - Hosted Pages disabled, artifact-only publish.
   - Hosted Pages enabled after a failed first publish, then `skip_collect` republish.
   - README generation in a private repository.
   - Plain mode rejection in public repositories.
   - Exact-tag and SHA-pinned action refs.

## Open Questions

- Should `skip_collect` publish with the exact action SHA recorded by the last collect even when the generated workflow itself now points at a newer major ref?
- If yes, should the action implement this by checking out and invoking the recorded action revision internally, or should republish intentionally use the current action only when it declares compatibility with the recorded data schema?
- Should user-owned GitHub App collection mode remain in the generated workflow, or should token minting be split into a separate documented advanced workflow variant?
- Should manual republish allow selecting an explicit collect workflow run ID, or is "latest retained data" sufficient for the default product?
- Should setup become an action mode before or after the combined workflow migration?

## Non-Goals

This ADR does not:

- introduce a Reponomics-owned GitHub App
- require automatic workflow-file mutation in user repositories
- remove exact-tag or SHA-pinned action consumption
- decide final v1 compatibility rules
- define a complete reusable-workflow architecture
- change the principle that users own their generated repository workflows, permissions, and secrets
