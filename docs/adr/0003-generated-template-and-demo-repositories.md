# ADR 0003: Generated Template And Demo Repositories

- Status: Accepted
- Date: 2026-04-28

## Context

The current branch model separates shipped template code, maintainer-only
validation, and demo/showcase assets across long-lived branches:

- `main` is the GitHub template branch users copy
- `template-dev` is the maintainer branch with tests and support tooling
- `demo` is the showcase branch with generated demo data and rendered outputs

That model has become hard to reason about. Product changes often need three
different promotions:

1. full source plus tests to `template-dev`
2. a stripped runtime/docs subset to `main`
3. generated mock data and demo outputs to `demo`

The problem is not that those surfaces differ. The problem is that the
differences are enforced by human discipline instead of deterministic build and
release automation.

The repository also needs a demo that proves the encrypted Pages mode as it
works in a real generated repository. A branch can show rendered HTML, but it
does not model a real template consumer with repository secrets, Pages settings,
artifact restore, encrypted payload rendering, and mock retained data.

## Decision

Replace the branch-based release model with a generated multi-repository model
plus a versioned runtime action:

1. `reponomics-dashboard-dev`
   - source of truth for development
   - contains tests, fixtures, demo-data generators, maintainer docs, and
     release automation
   - all human product work happens here

2. `reponomics-action`
   - versioned runtime action and optional reusable workflows
   - owns collection, artifact restore/upload, schema migration, encryption,
     README rendering, HTML dashboard rendering, and dashboard key rotation
   - published with semver tags so users can pin `v1`, exact releases, or SHAs

3. `reponomics-dashboard`
   - generated thin template repository
   - contains only onboarding docs, placeholder outputs, starter config, and
     workflow stubs that should be copied by **Use this template**
   - protected from direct human commits except emergency repair
   - updated by automation from an explicit source commit in the dev repo

4. `reponomics-dashboard-demo`
   - generated consumer repository created from the current template output
   - seeded with deterministic mock data
   - configured with demo-only repository secrets, including
     `DASHBOARD_SECRET_DO_NOT_REPLACE`
   - renders encrypted Pages output to demonstrate the unlock flow and artifact
     privacy model as users will experience it

The template and demo repositories are release artifacts. The dev repository is
the editable source.

Until the public launch/rebrand, the current repository names are:

- `reponomics-dashboard-dev` for editable source
- `reponomics-action` for the versioned runtime action
- `reponomics-dashboard` for the generated user template shell
- `reponomics-dashboard-demo` for the generated demo consumer

The source repository must also support local template and demo output under
`dist/` so dashboard and README UI work can be developed and reviewed before
publication. The external demo repository is a generated artifact, not a
development branch. The external action repository is the runtime update
channel, not a user data store.

Because the project is not public yet, the migration can be staged as a shadow
deployment. The existing repository can remain the temporary source while the
separate dev, runtime action, template, and demo repositories are built and
stabilized. If migration is the active priority, product work should pause
during that shadow deployment so the final sync is a verification step rather
than a reconciliation project. Maintainers can then decide whether the shadow
repository set is ready to become the public product surface.

## Release Flow

The dev repository owns release automation with these deterministic outputs:

1. Build and test the versioned runtime action.
2. Build the clean template tree from a checked-in allowlist.
3. Validate that forbidden paths are absent from the template output:
   maintainer tests, dev requirements, demo data, internal-only docs, and other
   non-template scaffolding.
4. Publish the generated tree to `reponomics-dashboard`.
5. Create or refresh `reponomics-dashboard-demo` from that same generated
   template tree.
6. Seed mock canonical CSV data in the demo repository.
7. Render the demo repository in encrypted Pages mode using the pinned runtime
   action and the demo repo's own `DASHBOARD_SECRET_DO_NOT_REPLACE`.
8. Commit provenance metadata recording:
   - dev source commit
   - runtime action version
   - template publish commit
   - demo seed version
   - publish workflow identity and timestamp

The demo refresh must not depend on live GitHub traffic collection. Mock data
is seeded deterministically so the showcase remains stable and reviewable.

The required local contract is:

- runtime action release checks validate at least collect and rotate-key modes.
- `make build-template` writes the clean template shell to `dist/template/`.
- `make verify-template` rejects forbidden files in `dist/template/`.
- `make build-demo` writes a generated consumer/demo tree to `dist/demo/`,
  keeps the live collection workflow disabled, seeds deterministic mock CSV
  data, and renders encrypted Pages output through the runtime action path.
- `make release-dry-run` builds both generated outputs without publishing.

## Rationale

This model aligns repository boundaries with product boundaries:

- the dev repo can be complex because it is for maintainers
- the runtime action can be versioned because it is the behavior and UI update
  channel
- the template repo can be boring because it is the shipped onboarding shell
- the demo repo can behave like a real user-created repository without
  polluting the template surface

It also improves the trust story. The template repository remains small and
auditable, while every generated update can point back to the exact dev commit
and build workflow that produced it. Users do not need to understand maintainer
test infrastructure or demo fixtures to inspect the template they will copy.

The demo repository becomes a stronger proof-of-concept than a demo branch
because it can carry real repository secrets and Pages configuration. The
encrypted dashboard payload is public, but the demo dashboard key is stored as
a GitHub Actions secret and is not committed, matching the intended product
model.

## Consequences

- Direct work on the template repository should stop. Changes are made in the
  dev repository and published through automation.
- The runtime action repository needs release discipline because it is the
  supply chain for collection, rendering, and rotation behavior.
- The template repository needs branch protection that allows the release bot
  to update `main` while discouraging human edits.
- The demo repository needs its own secrets and Pages configuration.
- Release automation must become part of the product's trusted computing base.
- Emergency fixes can still be applied to the template repo, but they must be
  backported to the dev repo immediately or they will be overwritten by the
  next generated release.
- The retired branch model documentation must not be shipped in the generated
  template output.
- Maintainer CI should run in the dev repository's default branch and may also
  run on the transitional `template-dev` branch while migration is underway.
- The migration is viable only if publication remains generator-driven:
  `template-manifest.yml`, generated-output tests, force-with-lease publishing,
  and repository settings enforcement must be treated as release gates rather
  than advisory maintainer conveniences.
- A generic encrypted-artifact-store action may be extracted later, but it is
  not part of the v1 launch scope. For v1, encrypted artifact restore, upload,
  and rotation stay inside the Reponomics runtime action.

## Non-Goals

This ADR does not specify final launch/rebrand names or exact branch protection
rules. The copy allowlist is implemented in `template-manifest.yml` and should
be treated as the source-to-template contract.

This ADR also does not require a separate demo repository forever. If the demo
remains small, it can start as a generated repository owned by the same release
workflow and later move to a dedicated organization or custom domain without
changing the core source-to-template publication model.

## Implementation Status, 2026-05-23

The generated-template model remains accepted. The runtime action repository is
now named `reponomics-dashboard-action`; older `reponomics-action` references
above are historical.

Current hardening is focused on the action/template pair:

- `reponomics-dashboard-dev` owns the generated-template source and docs.
- `reponomics-dashboard` remains the generated template target.
- `reponomics-dashboard-action` owns runtime behavior and is currently pinned
  by the template at `reponomics/reponomics-dashboard-action@v0.16.0`.
- `template-action-release.yml` records the accepted action release tag and
  target commit used to generate template workflow refs.

The separate generated demo repository remains deferred until a staging
consumer validates setup, collection, encrypted publish, CSV export, and key
rotation against the released action.
