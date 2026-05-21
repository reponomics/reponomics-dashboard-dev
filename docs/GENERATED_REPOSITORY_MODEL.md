# Generated Repository Model

This project treats repository boundaries as product boundaries.

- `reponomics-dashboard-dev`
  - editable source of truth
  - contains tests, release tooling, demo-data generation, maintainer docs, and
    implementation code
  - owns local generated outputs under `dist/template/` and `dist/demo/`

- `reponomics-dashboard`
  - generated thin template repository for **Use this template**
  - contains only onboarding docs, placeholder outputs, starter config, and
    workflow stubs listed in `template-manifest.yml`
  - should not receive normal human commits

- `reponomics-action`
  - versioned runtime action and optional reusable workflows
  - owns collection, artifact restore/upload, schema migration, encryption,
    README rendering, HTML dashboard rendering, and key rotation behavior
  - published with semver tags such as `v1` and patch/minor release tags

- `reponomics-dashboard-demo`
  - generated consumer-style demo repository
  - built from the thin template output
  - seeded with deterministic mock CSV data
  - rendered in encrypted Pages mode for product demonstration

During the pre-public shadow migration, the existing repository may temporarily
serve as the editable source until the shadow dev repository is validated and
the final sync is complete.

Current migration assumption: repository migration is the main priority. Product
feature work is paused until the shadow repository model is deployed, validated,
and either accepted or explicitly rejected.

## Local Release Contract

Run generated-output checks from the dev repository:

```bash
make build-template
make verify-template
make build-demo
make release-dry-run
```

`dist/template/` is the clean user template shell. `dist/demo/` is the
generated demo repository tree used for UI review and publication.

The demo repository is not a design or development branch. Dashboard and README
UI changes are made in the dev repository, reviewed through `dist/demo/`, and
then published as generated artifacts.

## Runtime Action Strategy

The public v1 template should not vendor the full Python runtime into every
user-created repository. Instead, the generated template should ship thin
workflows that call a versioned upstream runtime action:

```yaml
- uses: reponomics/reponomics-action@v1
  with:
    mode: collect
    traffic-token: ${{ secrets.TRAFFIC_TOKEN }}
    github-token: ${{ github.token }}
    readme-dashboard: enabled
    pages-dashboard: encrypted
  env:
    TRAFFIC_DASHBOARD_SECRET: ${{ secrets.TRAFFIC_DASHBOARD_SECRET }}
```

The action is the product runtime. The template is the onboarding and permission
surface. User repositories own their config, secrets, artifacts, generated
outputs, and selected runtime version.

The action should support at least these modes:

| Mode | Purpose | Primary writes |
|------|---------|----------------|
| `collect` | Restore prior data, collect GitHub traffic, merge, and encrypt/upload retained artifacts. | `traffic-data` artifact |
| `publish` | Restore retained data and render selected README/Pages outputs without collecting traffic. | `README.md`, hosted Pages artifact |
| `rotate-key` | Restore/decrypt with `TRAFFIC_DASHBOARD_SECRET`, re-render/re-encrypt with `TRAFFIC_DASHBOARD_NEXT_SECRET`, upload the rotated artifact, and summarize the manual promotion step. | rotated dashboard outputs, rotated `traffic-data` artifact |

The template should still provide friendly workflows for setup, scheduled
collection, publish-after-collect, manual republish, and key rotation because a
Marketplace action cannot define the repository's event schedule,
workflow-dispatch inputs, or permissions by itself. Those workflows should
remain small and explicit, delegating behavior to the runtime action.

The runtime action is also the UI update channel. Improvements to the dashboard,
README snapshot, schema migrations, artifact encryption, and GitHub API handling
ship through pinned action versions. The default template should pin `@v1`.
Advanced users can pin an exact release tag or commit SHA, or fork the action if
they want a different trust boundary.

The trust boundary should be documented plainly: using the template means
allowing the selected Reponomics runtime action version to run with
the permissions and secrets configured in the caller workflow.

## Dashboard Integrity

The dashboard should use browser-enforced subresource integrity for external
runtime assets wherever the generated HTML loads separate JavaScript or CSS
files. In practice, that means generated `<script>` or `<link>` tags should
include `integrity` and `crossorigin` attributes for CDN-hosted or otherwise
separate assets such as Chart.js.

This is an integrity check for subresources, not a full signature over the
top-level `docs/index.html` file. If an attacker can rewrite the HTML itself,
they can also remove or change subresource integrity metadata. The encrypted
dashboard payload is still authenticated by its encryption mode, so payload
tampering should fail to decrypt, but that does not by itself prevent a
modified shell from asking for or mishandling the dashboard key.

For v1, the practical requirement is:

- use SRI for any external JS/CSS dependencies
- prefer bundled or generated first-party assets when that gives a smaller
  trust surface than loading from a CDN
- keep the encrypted payload authentication check intact
- document that encrypted Pages protects the dashboard data, not the integrity
  of a compromised hosting surface

## Future Extraction: Encrypted Artifact Store

The encrypted artifact layer may have broader value as a standalone Marketplace
action, for example:

```yaml
- uses: reponomics/encrypted-artifact-store@v1
  with:
    mode: restore
    name: traffic-data
    path: data
  env:
    ARTIFACT_STORE_KEY: ${{ secrets.ARTIFACT_STORE_KEY }}
```

That could eventually provide generic `restore`, `save`, `rotate`, and
`inspect` modes for encrypted GitHub Actions artifacts. It is explicitly not a
v1 offering for the traffic dashboard launch. For v1, keep the encrypted
artifact implementation inside the Reponomics runtime action, but keep its
internal boundary clean enough to extract later.

## Viability Assessment

The repo-based model is viable, but only as a generated-release system. It
should not be treated as three ordinary repositories that humans edit by
convention. The model works when these invariants stay true:

- all product source changes land in `reponomics-dashboard-dev`
- `template-manifest.yml` is the only source-to-template membership contract
- `make verify` or an equivalent CI gate runs before any generated publish
- template and demo publishes use force-with-lease and target-repository checks
- repository settings are enforced after provisioning and periodically after
  GitHub settings drift
- emergency generated-repo edits are backported before the next publish

The current implementation already has the core mechanics: an allowlisted
template build, forbidden-path verification, deterministic demo generation,
disabled demo collection, release dry runs, force-with-lease publishing, and
repository-surface enforcement. Because the product is not public yet, the
preferred migration shape is a shadow deployment: build the target repositories
separately from the existing repository, stabilize them privately, and make the
public switch only after the runtime action, generated template, demo, and live
staging consumer have all proved the model. Since migration is the active
priority, the existing repository should accept only migration, verification,
and release-safety changes until the switch/no-switch decision is recorded. The
remaining migration work is operational: action packaging, remote naming,
branch/default-branch cleanup, repository settings, secrets, Pages
configuration, and provenance discipline.

## Risk Register

| Risk | Severity | Why it matters | Required control |
|------|----------|----------------|------------------|
| Publishing to the wrong repository | High | A generated publish force-updates the target branch. A mistaken remote could replace the dev source or demo repository with the wrong tree. | `publish_generated_repo.py` rejects remotes whose resolved repository name does not match the expected target. Release automation must set `TEMPLATE_REMOTE` and `DEMO_REMOTE` explicitly. |
| Branch-model residue | High | Keeping `main`, `template-dev`, and `demo` as meaningful release surfaces after cutover recreates the old ambiguity. | Keep old branch release behavior inactive, make the dev repo default branch explicit before switch-over, and document that generated repos replace the old branch roles. |
| Manifest drift | High | Runtime files can be omitted from the template or maintainer-only files can leak to users. | Update `template-manifest.yml` and `tests/test_generated_repos.py` together; keep `make verify` as the pre-publish gate. |
| Demo false confidence | Medium | A deterministic mock demo can prove rendering and encrypted Pages behavior, but not live token permissions, artifact restore edge cases, or GitHub API rate behavior. | Keep at least one staging consumer repository that runs real setup and live collection before public release. |
| Secret and Pages drift | Medium | The demo repository depends on repository secrets and Pages settings that are outside the git tree. | Run `make enforce-repo-policy`, manually confirm Pages and secrets after provisioning, and record those checks in the launch checklist. |
| Provenance gaps | Medium | Users and maintainers need to know which dev commit produced a generated template or demo publish. | Include the source commit in publish logs and commit messages now; add machine-readable provenance before unattended release automation. |
| Emergency generated-repo edits | Medium | Direct generated-repo fixes are overwritten by the next publish if not backported. | Treat emergency edits as temporary patches and open a dev-repo backport immediately. |
| Launch checklist optimism | Medium | Product capability can be ready while release topology is still transitional. | Track generated-repository cutover separately from core product readiness. |
| Premature switch-over | Medium | Renaming or replacing the current repository before the shadow trio is stable turns release-topology work into a product blocker. | Keep the existing repository as the source during shadow validation; make migration the only active workstream until the switch decision. |
| Migration scope creep | Medium | Once product work is paused, unrelated redesign or feature work hidden inside the migration extends the freeze and raises cutover risk. | Limit changes to repository topology, generated-output safety, settings, secrets, staging validation, and documentation needed for cutover. |
| Runtime/action boundary drift | High | Supporting both vendored scripts and the upstream action as first-class v1 paths would split testing and make user updates ambiguous. | Make the runtime action the single v1 behavior surface; keep template workflows thin and generated. |
| Over-extracting encrypted artifact storage | Medium | A generic encrypted-artifact action is attractive, but shipping it for v1 widens scope and delays the core dashboard launch. | Keep encrypted artifact storage inside the traffic runtime for v1; document standalone extraction as post-v1. |
| Dashboard integrity overclaim | Medium | Browser subresource integrity can reject modified external assets, but it cannot make a mutable top-level HTML file self-authenticating. | Use SRI for external runtime assets and keep the encrypted payload authenticated; document the remaining hosting-surface trust boundary plainly. |

## Maintainer Edit Protocol

After cutover, use the dev repository as the only normal editing surface.
During shadow migration, apply the same rule to the existing temporary source
repository until the final sync is complete. Generated repositories and `dist/`
outputs are review and publication artifacts.

| Change intent | Edit here | Generated effect |
|---------------|-----------|------------------|
| Change collected traffic fields or GitHub API behavior | `scripts/collect.py`, `scripts/storage.py`, `scripts/merge.py`, tests | Included in `dist/template/` and `dist/demo/` |
| Change the shipped collection workflow | `.github/workflows/collect.yml.disabled` | Copied as disabled workflow in both `dist/template/` and `dist/demo/`; users enable it through setup in their generated repositories |
| Change setup behavior | `.github/workflows/setup.yml` | Copied unchanged into both generated repositories |
| Change key rotation behavior | `.github/workflows/rotate-key.yml` | Copied unchanged into both generated repositories |
| Change template file membership | `template-manifest.yml` plus `tests/test_generated_repos.py` | Controls `dist/template/`; demo starts from that same tree |
| Change runtime action behavior | runtime action source plus action tests | Ships through action release tags such as `v1` |
| Change demo seed data | `scripts/generate_demo_data.py` | Written to `dist/demo/demo-data/` by `make build-demo` |
| Change dashboard UI | runtime renderer source, then review `dist/demo/docs/index.html` | Published action gets renderer code; demo gets rendered output |
| Change generated README UI | runtime README renderer source, then review `dist/demo/README.md` | Published action gets renderer code; demo gets rendered output |
| Change maintainer release commands | `maintainer.mk`, `scripts/build_template.py`, `scripts/build_demo.py`, `scripts/publish_generated_repo.py` | Stays out of generated template output |
| Change user-facing local runtime commands | `Makefile` | Ships to generated template users |

Do not edit these as sources of truth:

- `dist/template/`
- `dist/demo/`
- `reponomics-dashboard`
- `reponomics-action`
- `reponomics-dashboard-demo`
- generated `demo-data/` CSV files
- generated `docs/assets/` SVG files
- generated `README.md` or `docs/index.html` in demo output

If an emergency fix is made directly in a generated repository, immediately
backport it to the dev repository location listed above.

## Template Contract

The checked-in `template-manifest.yml` is the source-to-template contract. New
template shell files must be added there deliberately. Maintainer-only files,
runtime action internals, tests, internal docs, generated data, and release
tooling must stay out of the generated template output.

## Workflow Rule

The generated template repository ships the collection workflow as
`collect.yml.disabled` until a template user runs `setup.yml`. That workflow is
a thin launcher for the versioned runtime action. This prevents the template
repository itself from collecting and publishing live traffic by accident while
still giving generated repositories a guided path to enable collection.

Generated demo output also keeps live collection disabled and renders from
deterministic mock data through the runtime action so the showcase does not
depend on live GitHub traffic.

## Workflow Activation Matrix

| Repository | Product workflow/action files present | Product workflows enabled/runnable in this repo | Product workflows disabled or not present | GitHub-managed workflows | Notes |
|------------|--------------------------------|-----------------------------------------------|-------------------------------------------|--------------------------|-------|
| `reponomics-dashboard-dev` | maintainer CI, generated template workflow sources, runtime action source | `Maintainer CI` | Product setup/rotation launchers should not operate on dev analytics state | `Dependency Graph` may remain active | Human source work happens here. CI should validate source, generated template output, and runtime action packaging. |
| `reponomics-action` | `action.yml`, runtime source, optional reusable workflows | Runtime action tests and release workflows | No product collection against this repository's own traffic state | `Dependency Graph` may remain active | This is the versioned behavior and UI update channel. |
| `reponomics-dashboard` | `setup.yml`, `rotate-key.yml`, `collect.yml.disabled` thin launchers | None required in the source template repo | `Set up traffic dashboard`, `Rotate dashboard key`; collection must remain `.disabled` | `pages-build-deployment` may be active if Pages is enabled for docs | The files must exist so template users receive them. The source template repo itself should not collect, render, or rotate keys. |
| `reponomics-dashboard-demo` | `setup.yml`, `rotate-key.yml`, `collect.yml.disabled` thin launchers | None required | `Set up traffic dashboard`, `Rotate dashboard key`; collection must remain `.disabled` | `Dependency Graph` may remain active; Pages deployment may be active if Pages is configured | Demo is refreshed from the dev repo via `make build-demo` and `make publish-demo`, using deterministic mock CSV data rendered through the runtime action. |
| User-created repository from template | `setup.yml`, `rotate-key.yml`, `collect.yml.disabled` before setup; `collect.yml` after setup | `Set up traffic dashboard`; `Collect GitHub Traffic` after setup; `Rotate dashboard key` after setup when needed | `collect.yml.disabled` is removed/renamed by setup | Repository owner decides | This is the only normal place where live traffic collection should run. The workflow calls the pinned runtime action. |

If a workflow state needs to change, update this matrix first, then update the
generator or GitHub repository settings to match.

`Dependency Graph` and `pages-build-deployment` are GitHub-managed repository
services, not product workflow entry points. They may stay active when the
repository settings require them, but product collection, setup, and key
rotation must follow the table above.

## Repository Surface Policy

Repository settings are enforced with:

```bash
make enforce-repo-policy
```

The current policy keeps every repository surface narrow by disabling issues,
projects, wiki, discussions, downloads, most merge methods, and auto-merge
unless a repository explicitly needs them. GitHub only exposes fork-policy
updates through the repository API for organization-owned repositories, so fork
settings are not enforced for these personal-account repositories.

Security posture differs by repository:

- `reponomics-dashboard-dev`: pull requests and squash merges remain
  available for source review; vulnerability/dependency alerts enabled;
  Dependabot security updates are not forced by this script.
- `reponomics-action`: pull requests and release protections should
  be stricter than the generated repositories because this repository is the
  behavior and UI supply chain for users.
- `reponomics-dashboard`: pull requests and squash merges remain
  available for pre-launch review and repository health posture;
  vulnerability/dependency alerts enabled; Dependabot security updates are not
  forced by this script.
- `reponomics-dashboard-demo`: vulnerability/dependency alerts and
  Dependabot security updates disabled; pull requests disabled because the repo
  is generated, deterministic, and should not spend private-repo Actions time.
  GitHub requires at least one merge strategy even with pull requests disabled,
  so squash merge remains enabled as an inert setting.

GitHub documents pull request disabling as a repository feature toggle. The API
currently accepts `has_pull_requests=false` for this setting, even though that
field is newer than much of the published REST parameter table.

## Shadow Migration Plan

### 1. Freeze product work and keep the existing repository as the temporary source

- Pause product feature work in the existing repository until the migration is
  accepted or explicitly rejected.
- Allow only migration work, release-safety fixes, verification fixes, and
  documentation needed to complete the repository cutover.
- Tag or otherwise bookmark the start-of-freeze state so it is clear what
  changed during migration.
- Do not rename, repoint, or replace the existing repository as the first
  migration step.
- Keep branch-model release behavior inactive for public launch purposes while
  the shadow repository trio is being validated.

### 2. Provision the shadow repository set

- Create the intended dev, runtime action, template, and demo repositories as
  private or otherwise non-public shadow targets.
- Populate the dev repository from the existing repository source.
- Package and test the runtime action from the dev/source repository.
- Publish the template and demo repositories only through generated-output
  commands that point at the pinned runtime action version.
- In maintainer clones and CI, use explicit remotes for shadow targets. The
  publish commands must resolve `TEMPLATE_REMOTE` to the template repository
  and `DEMO_REMOTE` to the demo repository.

### 3. Validate generated outputs locally

Run:

```bash
make verify
make publish-template-dry-run
make publish-demo-dry-run
```

Review `dist/template/` for the thin user template surface and `dist/demo/` for
README, dashboard, encrypted Pages shell, and absence of live collection.

### 4. Package and validate the runtime action

- Build the runtime action with bundled Python scripts/renderers and declared
  action inputs.
- Validate `mode=collect` against deterministic demo data and a staging
  repository.
- Validate `mode=rotate-key` restores/decrypts with the current secret,
  re-renders/re-encrypts with the next secret, and emits clear promotion
  instructions.
- Validate dashboard integrity behavior: external assets have SRI metadata,
  tampered external assets are rejected by the browser, and tampered encrypted
  payloads fail to decrypt.
- Tag an internal or pre-release action version for shadow template workflows
  to pin.

### 5. Provision shadow repository settings

Run:

```bash
make enforce-repo-policy-dry-run
make enforce-repo-policy
```

Then manually confirm settings that are not fully captured by the GitHub API
script: default branches, branch protection, repository secrets, Pages source,
and any organization or personal-account settings that GitHub does not expose
through the same API fields.

### 6. Publish shadow template and demo repositories

- Publish the template first with `make publish-template`.
- Verify the template repository contains only expected shell files, no vendored
  runtime internals, and that `collect.yml` is still shipped as
  `collect.yml.disabled`.
- Publish the demo with `make publish-demo`.
- Verify the demo dashboard unlock flow, README summary, seeded CSV behavior,
  and Pages deployment.

### 7. Run a live staging consumer

- Create or refresh a staging repository from the generated template.
- Add real `TRAFFIC_TOKEN` and, for encrypted mode,
  `TRAFFIC_DASHBOARD_SECRET`.
- Run setup, confirm `collect.yml` is enabled only in the staging consumer, and
  confirm artifact restore works across a second run.

### 8. Decide whether to switch

Switch only if the shadow repository set meets the cutover acceptance criteria.
If the model proves too costly or confusing, keep the existing repository model
and use the shadow work as validation data rather than forcing a public
migration.

### 9. Final sync and verification

- Tag or otherwise bookmark the last pre-cutover state.
- Fast-forward or cherry-pick accepted migration changes into the shadow dev
  repository.
- Re-run `make verify`, publish template and demo artifacts again, and verify
  the staging consumer has not regressed.

### 10. Make the public switch

- Publish the runtime action with stable `v1` semantics.
- Make the shadow template repository public and mark it as the GitHub template
  repository.
- Make the demo public only after its Pages URL, unlock flow, and seeded output
  are acceptable.
- Point public documentation and repository descriptions at the new surfaces.
- Keep the old repository private or archived until recovery is no longer
  needed.
- Unfreeze product work only after the switch is complete or the no-switch
  decision has an explicit follow-up plan.

### 11. Retire old branch semantics

- Update repository descriptions, README maintainer notes, and contributor
  guidance so the generated-repository model is the only documented release
  path.
- Close or archive stale branch-model issues and docs.
- Delete obsolete release branches only after their final states are tagged or
  otherwise recoverable.

## Cutover Acceptance Criteria

- `make verify` passes in the dev repository.
- `make publish-template-dry-run` and `make publish-demo-dry-run` target the
  expected repositories.
- The runtime action has a tested collect mode and rotate-key mode, and the
  generated template pins a deliberate runtime version.
- The generated dashboard uses SRI for external runtime assets and does not
  claim that SRI protects against top-level HTML compromise.
- The template repository contains no maintainer docs, tests, dev
  requirements, demo data, release tooling, or vendored runtime internals.
- The demo repository contains seeded rendered output but no enabled live
  collection workflow.
- A staging consumer created from the template successfully runs setup and a
  second collection run.
- Repository settings and workflow states match the activation matrix above.
- Product work in the existing repository has remained paused except for
  migration, release-safety, and verification changes.
- A no-switch decision remains acceptable until these criteria are met.
