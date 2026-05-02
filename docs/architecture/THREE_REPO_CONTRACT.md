# Reponomics Three-Repository Architecture Contract

Version: 1.0 intended contract

This document describes the intended architecture. It is a design contract, not
an inventory of whatever happens to be implemented at a given moment.

## System Shape

Reponomics is split into three primary runtime/template repositories:

1. `reponomics-dashboard-dev`
2. `reponomics-dashboard`
3. `reponomics-action`

Reponomics should also have an umbrella product repository, likely named
`reponomics`, for the public project home. That repository is the thing people
star, share, discuss, and visit first. It does not replace the template
repository, because a template repo is primarily an installation surface rather
than a community or product narrative surface.

`reponomics-dashboard-demo` is intentionally excluded from the core contract
until the first three repositories are validated together. The demo should be
designed after the template/action integration is proven in a real staging
consumer.

The architectural rule is simple:

- `reponomics-dashboard-dev` is the human workspace and source of truth for the
  template product.
- `reponomics-dashboard` is a generated template artifact.
- `reponomics-action` is the runtime engine.
- an umbrella repo is the public product home.

Human changes should flow from dev source to generated template to user-created
consumer repositories. Runtime behavior should flow from the action into
consumer repositories through an explicitly pinned action ref.

## Why The Action Is Separate

The runtime action is separate primarily to create a clean versioning boundary.
Without a separate action repository, every user-created repository would copy
the runtime scripts at template creation time. Fixing bugs, improving the UI,
or changing artifact behavior would then require a per-repository migration
story. That is a poor fit for a template product whose runtime will need to
evolve.

The action repository lets Reponomics publish behavior independently from the
template shell:

- users get runtime fixes by moving from one action ref to another
- the template can stay thin and low-friction
- runtime tests and release discipline live next to the runtime code
- the trust boundary is explicit: users choose which action ref they allow to
  run with their workflow permissions and secrets

This split is not meant to hide behavior from users. The generated template
should make the action ref visible and document that it is part of the product
supply chain.

## Repository Contracts

### `reponomics-dashboard-dev`

Purpose:

- Own the template source, workflow stubs, docs, repository policy, and release
  tooling.
- Generate `reponomics-dashboard` as a clean template artifact.
- Provide a single workspace for changes to the template product.

Must contain:

- template source files
- `template-manifest.yml`
- maintainer build/publish tooling
- generated-template tests
- architecture and repository policy docs

Must not be:

- a live Reponomics consumer
- the runtime action implementation
- the generated template artifact
- the demo repository

Workflows:

- Maintainer CI may validate template generation and repository-policy checks.
- Product collection, setup, and key rotation workflows must not operate on
  `reponomics-dashboard-dev` analytics state.

Secrets:

- No product dashboard secrets are required for normal dev-repo validation.
- Publishing may require maintainer credentials through the local Git/GitHub
  environment, but those are release credentials, not product secrets.

Outputs:

- `dist/template/`, a generated filesystem artifact.
- Optional publish commits to `reponomics-dashboard`.

### `reponomics-dashboard`

Purpose:

- Be the GitHub **Use this template** repository.
- Contain the smallest useful onboarding surface for users.
- Copy cleanly into user repositories.

Must contain:

- `README.md`
- `config.yaml`
- `docs/README.md`
- `docs/SECURE_DASHBOARD_KEY.md`
- placeholder `docs/index.html`
- `.github/workflows/setup.yml`
- `.github/workflows/collect.yml.disabled`
- `.github/workflows/publish.yml.disabled`
- `.github/workflows/rotate-key.yml`
- license and ignore rules

Must not contain:

- Python runtime scripts
- runtime dependencies
- maintainer tooling
- tests
- generated demo data
- internal planning docs
- release/publish scripts

Workflows:

- `setup.yml` configures the caller repository for Reponomics.
- `collect.yml.disabled` is shipped disabled and becomes `collect.yml` only in
  user-created repositories after setup.
- `publish.yml.disabled` is shipped disabled and becomes `publish.yml` only
  when README or Pages publication is selected.
- `rotate-key.yml` launches dashboard/artifact key rotation.

Secrets:

- `TRAFFIC_TOKEN`: required before collection can run.
- `TRAFFIC_DASHBOARD_SECRET`: required when encrypted Pages or encrypted
  artifact mode is selected.
- `TRAFFIC_DASHBOARD_NEXT_SECRET`: temporary secret used only during rotation.

Outputs:

- In the template repository itself, no product data should be generated.
- In user-created repositories, workflows may commit README/dashboard outputs
  and upload retained data artifacts.

### `reponomics-action`

Purpose:

- Own runtime behavior.
- Provide the update channel for collection, artifact storage, encryption,
  rendering, schema handling, and key rotation.

Must contain:

- `action.yml`
- runtime source
- runtime tests
- action documentation
- release/versioning metadata

Must not contain:

- user repository config
- user secrets
- generated user data
- generated template release artifacts

Workflows:

- Action CI should validate runtime tests and action metadata.
- Release workflows may publish tags when the runtime contract is ready.

Secrets:

- The action repository should not require product secrets for normal tests.
- Consumer workflows pass secrets at runtime.

Outputs:

- GitHub Action metadata outputs.
- Files and artifacts written in the caller repository during action runs.

## Generated Template Flow

`reponomics-dashboard` is generated from `reponomics-dashboard-dev`.

The intended flow is:

1. Edit template source in `reponomics-dashboard-dev`.
2. Run local verification.
3. Build `dist/template/`.
4. Verify the generated tree contains only the template surface.
5. Publish `dist/template/` to `reponomics-dashboard`.

Direct edits to `reponomics-dashboard` are emergency-only. Any emergency edit
must be backported to `reponomics-dashboard-dev` before the next generated
publish.

## User Repository Flow

A user repository is created from `reponomics-dashboard`.

Initial state:

- `setup.yml` is available.
- `collect.yml.disabled` is present.
- `collect.yml` is absent.
- `publish.yml.disabled` is present.
- `publish.yml` is absent.
- `rotate-key.yml` is available.
- `README.md` is onboarding documentation.
- `docs/index.html` is a placeholder.
- No traffic artifact exists.

Setup state:

- The user adds required secrets.
- The user runs setup.
- Setup records the selected README/Pages/artifact modes.
- Setup enables collection by renaming or creating `collect.yml`.
- Setup enables publication by renaming or creating `publish.yml` only when
  README or Pages publication is selected.
- Setup commits workflow configuration changes.
- Setup does not collect or publish traffic data.

Collection state:

- Collection runs on schedule or manual dispatch.
- The action reads config and prior artifact state.
- The action collects, merges, and uploads retained data.

Publication state:

- Publication runs after collection when enabled, or manually when the user
  wants to republish from retained data.
- The action renders README and Pages outputs from retained data.
- The action optionally commits selected outputs.

Rotation state:

- The user adds `TRAFFIC_DASHBOARD_NEXT_SECRET`.
- The user runs rotation.
- Rotation re-encrypts retained state and dashboard output.
- The user manually promotes the next secret to the primary secret and deletes
  the temporary secret.

## Action Contract

The action should expose a narrow runtime contract.

### Inputs

`mode`:

- `doctor`
- `collect`
- `publish`
- `rotate-key`

Authentication inputs:

- `traffic-token`: token used for GitHub traffic and repository APIs.
- `github-token`: workflow/repository token used for artifact and repository
  operations.

Dashboard and artifact inputs:

- `dashboard-secret`
- `dashboard-next-secret`
- `readme-dashboard`: `disabled` or `enabled`
- `pages-dashboard`: `disabled`, `plain`, or `encrypted`
- `artifact-security-mode`: `plain`, `encrypted`, or `auto`
- `retention-days`

Repository visibility and dashboard disclosure are separate concepts. A public
repository can use an encrypted dashboard, and a private repository can choose
plain dashboard output. Use `plain` to mean unencrypted output, not "public."

Path inputs:

- `config-path`, default `config.yaml`
- `data-dir`, default `data`
- `dashboard-path`, default `docs/index.html`
- `readme-path`, default `README.md`

Commit input:

- `commit-outputs`, default `true`

### Environment Fallbacks

The action supports these fallbacks for template convenience and backwards
compatibility:

- `TRAFFIC_TOKEN`
- `GITHUB_TOKEN`
- `GH_TOKEN`
- `TRAFFIC_DASHBOARD_SECRET`
- `TRAFFIC_DASHBOARD_NEXT_SECRET`

Fallbacks must not obscure the token boundary. Traffic API authentication and
workflow/repository operations are different roles.

### Outputs

Action outputs are metadata, not the main product surface:

- `tracked-repos`
- `collected-at`
- `artifact-mode`
- `dashboard-mode`
- `readme-updated`
- `dashboard-updated`
- `schema-version`
- `runtime-version`

The main product surface is the caller repository's committed outputs and
retained artifacts.

## Action Modes

### `doctor`

Purpose:

- Validate setup choices without collecting, rendering, publishing, rotating,
  or committing product outputs.

Reads:

- caller repository `config.yaml`
- selected workflow inputs
- caller repository metadata
- secrets passed by the workflow

Writes:

- workflow summary
- action metadata outputs

Required secrets:

- `traffic-token` or `TRAFFIC_TOKEN` when collection is being enabled
- `dashboard-secret` or `TRAFFIC_DASHBOARD_SECRET` when encrypted retained
  artifacts or encrypted Pages output are selected

Required behavior:

- Validate token presence and basic authentication.
- Validate required secrets for selected modes.
- Validate dashboard secret strength when a secret is required.
- Resolve `artifact-security-mode=auto`.
- Explain the effective privacy boundary in the workflow summary.
- Fail before setup enables scheduled collection when required inputs are
  missing or incoherent.

### `collect`

Purpose:

- Collect GitHub traffic data and maintain retained canonical state.

Reads:

- caller repository `config.yaml`
- prior `traffic-data` artifact if present
- caller repository metadata
- GitHub traffic API data
- secrets passed by the workflow

Writes:

- updated retained artifact
- workflow summary
- action metadata outputs

Required secrets:

- `traffic-token` or `TRAFFIC_TOKEN`
- `dashboard-secret` or `TRAFFIC_DASHBOARD_SECRET` when encrypted Pages or
  encrypted artifacts are active

Required behavior:

- Refuse to run while `TRAFFIC_DASHBOARD_NEXT_SECRET` is set.
- Restore prior data before collecting.
- Treat missing prior artifact as first run.
- Preserve normalized CSV as the canonical reporting input.
- Upload refreshed retained state after merge/retention.
- Never publish README or Pages output by itself. The template may run
  `publish` after successful collection when the user explicitly enabled
  publication.

### `rotate-key`

Purpose:

- Rotate encrypted dashboard/artifact state from the current key to the next
  key without collecting new traffic.

Reads:

- current retained artifact
- current dashboard secret
- next dashboard secret
- current workflow/dashboard mode configuration

Writes:

- re-rendered dashboard output encrypted with the next key
- retained artifact encrypted with the next key
- optional README/dashboard commit
- workflow summary with manual promotion instructions

Required secrets:

- `dashboard-secret` or `TRAFFIC_DASHBOARD_SECRET`
- `dashboard-next-secret` or `TRAFFIC_DASHBOARD_NEXT_SECRET`

Required behavior:

- Must not collect new traffic.
- Must not rewrite repository secrets.
- Must fail clearly if the current or next key is missing.
- Must fail clearly when no encrypted dashboard/artifact mode is active.
- Must leave the repository in a state where the user must manually promote the
  next key and delete the temporary key.

### `publish`

Purpose:

- Render and publish outputs from already-retained data without collecting new
  GitHub traffic.

Why it belongs as a separate mode:

- Collection and publication are conceptually distinct.
- Some users may want artifact-backed traffic history without publishing a
  README summary or Pages dashboard.
- A separate publish mode makes accidental data exposure easier to reason
  about: collection can be enabled while publication remains disabled.
- It gives users a clean way to change presentation settings after data has
  already been collected.

Reads:

- existing retained artifact
- caller repository configuration
- selected README/Pages publication modes
- dashboard secret when encrypted output is selected

Writes:

- `README.md`, if README publication is enabled
- `docs/index.html`, if Pages publication is enabled
- `docs/assets/*`, when README metrics are enabled
- optional standalone dashboard artifact when Pages mode is plain
- optional commit to the caller repository

Required behavior:

- Must not collect new traffic.
- Must not mutate retained data except for schema migration if migration is
  explicitly part of the runtime contract.
- Must allow "store only" operation by keeping publish modes disabled.
- Must support rich static README dashboards, not only short summaries.

## Template Workflow Contracts

### Setup Workflow

Purpose:

- Configure the caller repository to use Reponomics.

Intended responsibilities:

- Call `reponomics-action` with `mode: doctor`.
- Validate required secrets for the selected modes.
- Resolve `readme-dashboard`, `pages-dashboard`, and `artifact-security-mode`.
- Enable collection by renaming or creating `collect.yml`.
- Enable publication by renaming or creating `publish.yml` only when README or
  Pages publication is selected.
- Persist selected mode values into the collection workflow or another
  explicit config surface.
- Commit setup/configuration changes.

Non-responsibilities:

- It should not own collection semantics.
- It should not own rendering semantics.
- It should not own key rotation semantics.
- It should not trigger an immediate first collection or publication.

Decision:

- Setup stops after validating, configuring, and enabling the selected
  workflows. The first collection is a normal `collect` workflow run.

Tradeoffs:

- Immediate first collection gives users fast feedback and proves that secrets,
  permissions, artifact storage, rendering, and commits work before they leave
  setup. It also avoids a confusing state where setup succeeds but the first
  scheduled collection fails hours later because a token or dashboard secret was
  missing or misunderstood.
- Immediate first collection is riskier because setup is the moment when users
  are least likely to understand the privacy consequences. A user may choose an
  unsafe publication mode, provide a weak dashboard secret, or misunderstand
  whether metrics will be written in plaintext. Running collection immediately
  can turn that misunderstanding into published output before the user has
  reviewed the configured workflow.
- Delayed first collection keeps setup as a pure configuration step and gives
  users a natural pause to review `collect.yml`, repository secrets, Pages
  settings, and publication choices.
- Delayed first collection can create a different failure mode: collection may
  be enabled on a schedule, the user walks away, and the first run happens six
  hours later with incomplete or mistaken configuration.

- To reduce delayed-run risk, setup should validate that required secrets exist,
  that the traffic token is usable enough to authenticate, and that encrypted
  modes have a dashboard secret of acceptable strength. Setup should also make
  the next required action explicit in the workflow summary.

### Collection Workflow

Purpose:

- Schedule and manually run normal traffic collection.

Responsibilities:

- Run only from the intended default branch.
- Refuse incomplete key rotation.
- Check out the caller repository.
- Call `reponomics-action` with `mode: collect`.
- Call `reponomics-action` with `mode: publish` after successful collection
  only when publication is enabled.
- Pass selected modes and required secrets.

Non-responsibilities:

- It should not contain runtime Python implementation.
- It should not duplicate rendering, artifact, or schema logic.

### Publish Workflow

Purpose:

- Manually render selected output surfaces from retained data without
  collecting new traffic.

Responsibilities:

- Check out the caller repository.
- Restore retained artifact state through `reponomics-action`.
- Call `reponomics-action` with `mode: publish`.
- Pass selected README/Pages modes and required dashboard secret.
- Optionally commit selected outputs.

Non-responsibilities:

- It should not collect traffic.
- It should not rotate keys.
- It should not duplicate renderer internals.

### Rotation Workflow

Purpose:

- Launch encrypted dashboard/artifact key rotation.

Responsibilities:

- Require explicit user confirmation.
- Ensure collection has been set up.
- Load the currently selected modes.
- Call `reponomics-action` with `mode: rotate-key`.
- Pass current and next dashboard secrets.

Non-responsibilities:

- It should not collect traffic.
- It should not rewrite repository secrets.
- It should not duplicate encryption/rendering internals.

## Secrets Matrix

| Repository | Secret | Required? | Purpose |
|------------|--------|-----------|---------|
| `reponomics-dashboard-dev` | none for normal verification | no | Template generation should not require product secrets. |
| `reponomics-dashboard` | none in template repo itself | no | The template repository should not collect product data. |
| user-created repo | `TRAFFIC_TOKEN` | yes for collection | GitHub traffic and repository APIs. |
| user-created repo | `TRAFFIC_DASHBOARD_SECRET` | yes for encrypted modes | Dashboard and retained artifact encryption. |
| user-created repo | `TRAFFIC_DASHBOARD_NEXT_SECRET` | only during rotation | Temporary next encryption key. |
| `reponomics-action` | none for normal CI | no | Runtime tests should use fixtures/mocks unless explicitly running live validation. |

## Outputs Matrix

| Repository | Produces | Notes |
|------------|----------|-------|
| `reponomics-dashboard-dev` | `dist/template/` | Generated artifact source for `reponomics-dashboard`. |
| `reponomics-dashboard` | template copy surface | No live data should be generated here. |
| user-created repo | README, dashboard, assets, retained artifact | Product outputs live with the user. |
| `reponomics-action` | action metadata and runtime releases | Runtime behavior, not user data. |

## Versioning Contract

Before public release, template workflows may reference a mutable pre-release
ref such as `reponomics/reponomics-action@main`.

For public release, template workflows should reference a stable tag such as
`@v1` or a deliberate pre-1.0 tag. Users who want maximum supply-chain
stability can pin a full commit SHA.

The template should document that the selected action ref is part of the trust
boundary.

## Demo Repository

`reponomics-dashboard-demo` is not part of the initial core contract.

Possible models:

1. Create it from `reponomics-dashboard` exactly like a user repository, then
   run setup/collection against controlled demo data or a demo account.
2. Generate it from `reponomics-dashboard-dev` using seeded deterministic data.
3. Maintain both a generated seeded showcase and a live staging consumer.

The decision should be made after a private staging consumer validates:

- `reponomics-dashboard-dev` can generate `reponomics-dashboard`
- `reponomics-dashboard` can create a usable repository
- `reponomics-action` can perform collection and rotation from that repository

## Design Risks To Watch

- Setup accumulating runtime behavior instead of remaining configuration.
- The action token contract collapsing traffic API access and repository
  workflow operations into one ambiguous token.
- Direct edits to generated `reponomics-dashboard`.
- Demo requirements forcing complexity back into the template.
- Mutable pre-release action refs being mistaken for a public stability
  guarantee.
