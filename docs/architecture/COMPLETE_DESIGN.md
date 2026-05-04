# Reponomics Complete Architecture

Version: 1.0 intended design

This document is the resolved product architecture for the pre-release repo
split. It describes the contract Reponomics should build toward. The current
implementation gap is tracked separately in
[Current Implementation Gap Map](CURRENT_IMPLEMENTATION_GAP_MAP.md).

## Product Thesis

Reponomics is a repo-native GitHub traffic analytics product.

The product should let a user create a repository from a template, add a
traffic token and optional dashboard secret, and then collect durable GitHub
traffic history without adopting an external analytics service. The retained
data belongs to the user's repository. The rendering and collection behavior is
delivered by a versioned action.

The core promise is:

- no third-party database in the default path
- normalized CSV remains the canonical reporting input
- the user owns config, secrets, retained artifacts, committed outputs, and the
  action ref they trust
- Reponomics can keep shipping richer metrics and dashboards without asking
  existing users to copy runtime files from a template repository

## Repository Map

Reponomics should have four product-facing repositories:

| Repository | Role | Maintained how |
|------------|------|----------------|
| `reponomics` | Umbrella product home, docs, roadmap, issues, discussions, and the repository people star/share. | Human-maintained. |
| `reponomics-action` | Runtime engine and main update channel. | Human-maintained runtime package. |
| `reponomics-dashboard-dev` | Source workspace for the generated template artifact. | Human-maintained template source/build repo. |
| `reponomics-dashboard` | GitHub template repository users copy. | Generated from `reponomics-dashboard-dev`. |

`reponomics-dashboard-demo` should be created after the core integration is
proven. It is a showcase/staging surface, not part of the core architecture
contract.

## Why The Action Is Separate

The separate action repo is primarily a versioning and update boundary.

If the template ships runtime scripts directly, every user-created repository
freezes those scripts at creation time. Any later dashboard improvement, metric
fix, schema migration, or collection change becomes a per-user file-copy
problem. That is a poor fit for a product that expects to keep adding widgets,
data families, privacy controls, and rendering polish.

The action repo solves that by making runtime behavior versioned:

- compatible updates can move through `reponomics-action@v1`
- cautious users can pin exact tags or commits
- runtime tests, fixtures, release notes, and security review live next to the
  runtime code
- the template stays thin and understandable
- the trust boundary is explicit: the user chooses which action ref may run
  with repository permissions and secrets

This is not an attempt to hide behavior. The template should show the action ref
plainly and explain that the action is part of the trusted product supply
chain.

## Ownership Boundaries

The most important boundary is:

- user repositories own data, config, secrets, artifacts, committed outputs,
  repository settings, and version pinning
- `reponomics-action` owns collection, artifact restore/upload, encryption,
  schema migration, rendering, README asset generation, Pages output, and key
  rotation
- `reponomics-dashboard-dev` owns template workflow shells, onboarding docs,
  config defaults, generated-template tests, and publish tooling
- `reponomics-dashboard` is only the generated install artifact
- `reponomics` owns product narrative, support, roadmap, release notes, and
  high-level docs

The template must not contain Python runtime internals or renderer templates.
It should contain only the workflow shell, config defaults, placeholder docs,
and onboarding instructions needed to start.

## User Personas

### Vibe Coder

This user is building something quickly, may be coming from a chat-based coding
workflow, and may not know what a workflow file is.

The product should give them:

- a visible product home at `reponomics`
- a "Use this template" path that does not require local tooling
- setup profiles instead of raw low-level settings
- a static key generator page that never sends generated key material to a
  server
- a setup workflow that validates secrets and permissions before enabling
  scheduled collection
- clear wording about who can see README metrics, Pages metrics, and retained
  artifacts
- a default action ref that receives compatible updates automatically

The setup flow must not assume they understand plaintext, Git history,
artifact retention, or Pages visibility. It should explain the consequences of
their chosen profile before any collection or publishing happens.

### Senior Engineer

This user wants control, auditability, and freedom to customize.

The product should give them:

- exact action pinning by tag or commit SHA
- explicit token separation between traffic API access and repository workflow
  operations
- store-only mode with no README or Pages publication
- manual publish runs from retained artifacts
- local/offline rendering and inspection path after v1 if demand justifies it
- clear schema/version metadata
- advanced config that can override default output paths, retention, action
  modes, and publication choices
- eventual renderer override hooks with compatibility diagnostics

The product should not force this user through a high-level wizard, but the
same privacy model should still be legible from config and workflow files.

## Action Modes

The public action contract should expose three product operations:

- `collect`
- `publish`
- `rotate-key`

Validation is not a separate public action mode. Setup validation belongs to
the setup workflow. Collection validation belongs to `collect`. Publication
validation belongs to `publish`. Rotation validation belongs to `rotate-key`.
Shared validation helpers can exist internally, but they are implementation
details rather than workflow-level verbs.

### `collect`

Purpose:

- collect GitHub traffic data and maintain retained canonical state

Reads:

- caller repository config
- prior `traffic-data` artifact, if present
- GitHub traffic and repository APIs
- traffic token

Writes:

- refreshed retained artifact
- action outputs
- workflow summary

Required behavior:

- validate traffic token presence and basic authentication
- validate that retained artifact encryption settings are coherent
- fail encrypted retained-artifact runs when the dashboard secret is below the
  policy entropy threshold unless `allow-weak-dashboard-secret` is true
- treat missing prior artifact as first run
- restore and decrypt prior retained state when needed
- collect required v1 data families: views, clones, top referrers, top paths
- merge into normalized CSV
- apply retention rules
- upload retained artifact in the resolved artifact security mode
- refuse to run while a key rotation is half-configured

`collect` should not publish README or Pages output by itself. The template may
run `publish` immediately after a successful `collect` when the user explicitly
enabled publication, but the runtime concepts remain separate.

### `publish`

Purpose:

- render selected output surfaces from already-retained data

Reads:

- current retained artifact
- caller repository config
- selected README and Pages publication modes
- dashboard secret when encrypted output is selected

Writes:

- `README.md`, when README dashboard is enabled
- `docs/index.html`, when Pages dashboard is enabled
- `docs/assets/*`, when README assets are enabled
- optional standalone dashboard artifact
- optional commit to the caller repository
- action outputs and workflow summary

Required behavior:

- validate that publication modes are coherent
- validate dashboard secret presence when encrypted Pages output is selected
- fail encrypted Pages publication when the dashboard secret is below the
  policy entropy threshold unless `allow-weak-dashboard-secret` is true
- never write entropy estimates, weak-secret labels, or override diagnostics
  into generated README, Pages, or retained artifact outputs
- never call GitHub traffic APIs
- never collect new data
- render README and Pages from the same normalized data
- preserve `plain` versus `encrypted` terminology
- support a rich static README dashboard, not only a short summary
- leave retained data untouched except for explicit, compatible schema
  migration

`publish` is the main rendering update surface. New widgets, visual polish,
README charts, Pages UI changes, and compatible dashboard features should ship
through action updates here.

### `rotate-key`

Purpose:

- rotate encrypted retained artifacts and encrypted dashboard output from the
  current dashboard secret to a next dashboard secret

Reads:

- current retained artifact
- current dashboard secret
- next dashboard secret
- current publication/storage configuration

Writes:

- retained artifact encrypted with the next key
- encrypted dashboard output encrypted with the next key, when Pages encrypted
  mode is active
- optional committed output updates
- workflow summary with manual secret-promotion instructions

Required behavior:

- never collect new traffic
- never rewrite GitHub repository secrets
- fail if current or next key is missing
- fail when the next dashboard secret is below the policy entropy threshold
  unless `allow-weak-dashboard-secret` is true
- fail if no encrypted retained artifact or encrypted dashboard output exists
- leave the user with explicit instructions to promote
  `TRAFFIC_DASHBOARD_NEXT_SECRET` to `TRAFFIC_DASHBOARD_SECRET` and then delete
  the temporary secret

## Template Workflow Shape

The generated template should include thin workflow shells. Runtime logic lives
in the action.

### `setup.yml`

Responsibilities:

- accept user setup profile choices
- require explicit confirmations for any plain committed or hosted output
- run setup validation before enabling scheduled workflows
- validate traffic token presence and basic authentication when collection is
  being enabled
- validate dashboard secret presence when encrypted retained artifacts or
  encrypted Pages output are selected
- fail encrypted profiles when the dashboard secret is below the policy entropy
  threshold unless the user explicitly selects the weak-secret override
- persist the weak-secret override into the enabled workflows if the user
  chooses it
- warn that, in repositories with public read access, the override flag,
  workflow logs, workflow summaries, and annotations may publicly advertise
  that the encrypted data is easier to brute force
- explain the effective privacy boundary in the workflow summary
- persist selected modes into config/workflow variables
- enable collection only after validation passes
- enable the separate publish workflow only when the selected profile publishes
  README or Pages output
- commit setup changes
- write a clear workflow summary with the next manual step and expected
  schedule

Non-responsibilities:

- no traffic collection
- no dashboard publishing
- no key rotation
- no renderer logic

Setup should not trigger an immediate first collection. The risk is that setup
is precisely when the user is least likely to understand what will be
committed, hosted, encrypted, or retained. The counter-risk is that a scheduled
run may fail later if secrets are wrong, so setup must not enable scheduled
collection unless required secrets and token checks pass.

### `collect.yml`

Responsibilities:

- scheduled and manual traffic collection
- call `reponomics-action` with `mode: collect`
- refuse to run during incomplete key rotation

Store-only users should keep publication disabled. Their workflow should still
collect retained artifacts without committing README or Pages metrics.

### `publish.yml`

Responsibilities:

- run on `workflow_run` after successful completion of the collect workflow
- support manual `workflow_dispatch` republish from retained artifacts
- allow users to change presentation settings and regenerate outputs without
  collecting new traffic
- support publication-only validation during staging

The generated template may ship this as `publish.yml.disabled` and let setup
enable it only when README or Pages publication is selected.
Keeping publication in its own workflow lets a repository owner disable
publication directly from the GitHub Actions UI without disabling collection.

### `rotate-key.yml`

Responsibilities:

- manual encrypted state rotation
- require explicit confirmation
- call `reponomics-action` with `mode: rotate-key`
- write promotion instructions

The workflow must not mutate repository secrets. GitHub intentionally treats
secrets as write-only from the UI/API perspective, and Reponomics should keep
that trust boundary clear.

## Secrets And Tokens

User-created repositories need:

| Secret or token | Required when | Purpose |
|-----------------|---------------|---------|
| `TRAFFIC_TOKEN` | collection is enabled | GitHub traffic and repository metadata APIs. |
| `GITHUB_TOKEN` | normal workflow operation | Checkout, commits, artifacts, workflow operations. Usually provided by GitHub Actions. |
| `TRAFFIC_DASHBOARD_SECRET` | encrypted retained artifacts or encrypted Pages output | Encrypt/decrypt retained state and encrypted dashboard payloads. |
| `TRAFFIC_DASHBOARD_NEXT_SECRET` | key rotation only | Temporary next key during rotation. |

Action inputs should preserve the same separation:

- `traffic-token` for GitHub traffic/repository APIs
- `github-token` for artifact, commit, and workflow operations
- `dashboard-secret` for current encryption
- `dashboard-next-secret` for rotation
- `allow-weak-dashboard-secret`, default `false`, to explicitly bypass the
  dashboard secret entropy gate

Environment fallbacks may exist for convenience, but they must not blur the
roles.

Dashboard secret entropy checks are intentionally a product guardrail, not a
cryptographic proof. The default policy should reject obviously weak or
human-chosen secrets for encrypted modes, while allowing an explicit
`allow-weak-dashboard-secret: true` override for users who understand and
accept the risk. The override never bypasses secret presence, decryptability, or
encryptability checks.

The weak-secret override has its own disclosure risk. In a public repository,
committed workflow files, workflow inputs, logs, summaries, annotations, and
action outputs should be treated as publicly observable. If the override is
visible, an attacker can use it as a signal that the encrypted traffic payload
may be brute-forceable. Reponomics cannot warn a public-repo user secretly from
inside GitHub Actions, so the setup UX and key-generation docs must explain
this tradeoff before the user enables the override. Runtime and generated
outputs should avoid adding unnecessary weak-secret signals beyond the explicit
override state needed to run.

## Privacy Model

Repository visibility, output disclosure, and artifact encryption are separate
dimensions.

Use:

- `plain` for unencrypted output or retained data
- `encrypted` for encrypted output or retained data
- `public` only for repository/product visibility, not as a synonym for
  plaintext

The setup UI should present intent profiles first:

- Store only
- Private README dashboard
- Keyed dashboard
- Plain hosted dashboard
- Fully open metrics

Then it should show the derived settings:

- repository visibility detected from GitHub
- README dashboard enabled/disabled
- Pages dashboard disabled/encrypted/plain
- artifact mode encrypted/plain
- who can see each surface
- whether data is committed to git
- whether data exists only as an artifact
- whether the user can delete retained data by deleting artifacts

`artifact-security-mode=auto` should be conservative:

- choose `encrypted` for public repositories unless the user explicitly chooses
  a fully open profile or explicitly sets artifact mode to `plain`
- choose `encrypted` whenever Pages output is encrypted
- choose `plain` for private/internal store-only or README-only profiles only
  when the setup profile treats repository read access as the intended privacy
  boundary
- never infer that plain Pages output means plain retained artifacts

## Rendering And Feature Delivery

Rendering must be action-owned.

The generated template should not ship dashboard renderer scripts. Existing
users should receive compatible renderer improvements by updating the action
ref, not by copying files from `reponomics-dashboard`.

Examples of compatible action-delivered improvements:

- new README SVG charts derived from existing retained data
- new Pages widgets derived from existing retained data
- visual polish and layout improvements
- release-date overlays derived from data already available to the runtime
- additive schema migrations that run automatically
- optional new data families that degrade gracefully when unavailable

Examples of changes that require migration notes or a major version:

- changing privacy defaults
- changing committed output paths without compatibility shims
- requiring a new secret or broader token permission
- requiring workflow changes in existing repositories
- removing a mode, input, output, config key, or supported artifact schema
- changing what `plain`, `encrypted`, or `disabled` means

Advanced customization can come later through explicit renderer profiles or
local overrides, but the default path should optimize for users receiving
compatible improvements through the action.

## Versioning Policy

Pre-release:

- integration repositories may use `reponomics/reponomics-action@main`
- staging may pin exact commits while debugging
- public-looking tags should stay below v1 until the contract is validated

Public release:

- generated template workflows should reference a stable major tag such as
  `reponomics/reponomics-action@v1`
- compatible releases move the `v1` tag
- users who need strict supply-chain stability can pin exact release tags or
  commit SHAs
- release notes must say whether existing users receive the change through the
  action ref or need template/workflow migration

Template updates:

- affect newly created repositories automatically
- do not automatically change existing user repositories
- should be rare after v1 because runtime/rendering changes belong in the
  action
- require explicit migration notes when existing repositories should copy a
  workflow/config/docs change

## Dashboard Dev Operations

`reponomics-dashboard-dev` needs stronger release credentials than a normal
template consumer because it publishes generated artifacts and may enforce repo
policy.

Short term:

- maintainer local auth or a fine-grained org PAT restricted to Reponomics
  repositories is acceptable for private pre-release operations

Long term:

- use a Reponomics GitHub App for release/policy operations
- grant only the repository permissions needed for publishing generated
  template commits, setting template status, and enforcing repository policy
- keep product traffic tokens and dashboard secrets out of
  `reponomics-dashboard-dev`

## Local And Offline Path

The primary path remains GitHub Actions. A local path is useful for senior
engineers and privacy-sensitive users, but it should not complicate v1
onboarding.

The eventual local path should support:

- downloading/restoring retained artifacts
- decrypting locally with a dashboard secret
- rendering local HTML without committing
- inspecting config and privacy consequences
- optionally uploading a refreshed encrypted artifact

This can be implemented as an action-invoked module first, then exposed as a
CLI later if demand is real.

## Migration Readiness Criteria

The repo split is ready for live staging only when:

- `reponomics-action` supports the intended mode contract or the gap is
  explicitly accepted for pre-release testing
- generated template workflows call the action and contain no runtime internals
- setup validates configuration without collecting or publishing
- store-only, README-only, encrypted Pages, plain Pages, and key-rotation
  profiles are understood in docs and tests
- dashboard rendering is action-owned
- token boundaries are split
- terminology uses `plain` for unencrypted output
- current gaps are tracked in the gap map

After that, the right next validation is a private staging repository created
from `reponomics-dashboard`, followed by setup, collect, publish, and rotate-key
runs against controlled repositories.
