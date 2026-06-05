# Reponomics Dashboard

The Reponomics Dashboard provides GitHub maintainers with a convenient and cost-free way to collect and analyze GitHub traffic data beyond GitHub's rolling traffic window, as well as other growth metrics, and renders a GitHub-native dashboard that can be hosted privately in encrypted form via GitHub Pages. A repository created from this template collects views, clones, top referrers, popular paths, and repository growth counters into retained GitHub Actions artifacts. The HTML dashboard is rendered during the publish workflow; it is deployed to GitHub Pages only when hosted dashboard publication is enabled, and otherwise remains a downloadable workflow artifact. Retained dashboard data is not committed to the repository, unless the user opts in to a more lightweight dashboard that is rendered to their README. This is only available for private repos.

The template is intentionally thin. Collection, artifact handling, schema migration, encryption, dashboard rendering, CSV export, key rotation, incident reset behavior, and managed local documentation sync are owned by the versioned action:

```yaml
uses: reponomics/reponomics-dashboard-action@v0.18.0
```

> [!WARNING]
> Public pre-release: this repository is visible for review and hardening, but it is not yet promoted for general use. Do not expect stable behavior or seamless upgrades before `v1`. Documentation should also not be considered authoritative as of yet.

## Setup

1. Create a repository from this template.
2. Create a token and add it as a repository secret named `COLLECTION_TOKEN` (NOTE: see below for instructions regarding the use of a GitHub App installation token instead.) [Create a fine-grained personal access token](https://github.com/settings/personal-access-tokens/new?name=COLLECTION_TOKEN&description=Read%20repository%20data%20for%20Reponomics%20Dashboard&expires_in=366&administration=read), choose the owner whose repositories should be collected, and keep the prefilled repository permission `Administration: read`. Choose **All repositories** for broad automatic discovery, or **Only selected repositories** if you want to limit collection to specific repositories. If you choose selected repositories, keep `config.yaml` within that token's repository access. If this dashboard must track repositories under multiple GitHub users or organizations, read [Token Scope And Repository Owners](#token-scope-and-repository-owners) before choosing a token. Do not grant Pages or Administration write permissions to this token for dashboard setup. Setup uses the workflow `GITHUB_TOKEN` to commit workflow enablement changes in this repository.
3. Choose a privacy mode:
   - `strong`: encrypted retained artifacts and encrypted dashboard output; requires a generated high-entropy `DASHBOARD_SECRET_DO_NOT_REPLACE`.
   - `casual`: encrypted retained artifacts and encrypted dashboard output; accepts any non-empty `DASHBOARD_SECRET_DO_NOT_REPLACE`, but is not intended to resist targeted offline guessing.
   - `plain`: plaintext retained CSV artifacts; private repositories only and no hosted Pages dashboard.
4. For `strong` or `casual`, add `DASHBOARD_SECRET_DO_NOT_REPLACE` and store the same value somewhere private. See [Secure Dashboard Key Generation](docs/SECURE_DASHBOARD_KEY.md).
5. Run **Actions -> Set up Reponomics dashboard -> Run workflow**.
6. If you enabled hosted dashboard publication, open this repository's **Settings -> Pages** page and set **Build and deployment -> Source** to **GitHub Actions**. If GitHub suggests workflow templates, skip them; the Reponomics publish workflow already deploys the Pages artifact.

> [!NOTE]
> We chose the deliberately outlandish name `DASHBOARD_SECRET_DO_NOT_REPLACE` because the Actions > Secrets UI does not provide another affordance where we can warn users that if they want to rotate their secret, simply overwriting the existing secret is not the correct way to do so, and will in fact result in permanent data loss if the previous secret was not retained by the user.

Setup enables the collection workflow, the manual incident reset workflow, and a scheduled workflow keepalive, writes a static post-setup README, and leaves hosted Pages publication disabled unless `generate_html_dashboard` is enabled during setup. Metric README dashboard generation is private-repository only and disabled unless `generate_readme` is enabled during setup. Setup does not collect traffic immediately. Collection runs twice daily on `main`; when publishing or README generation is enabled, collection uploads a small provenance artifact and the separate publish workflow renders from that exact collect run's dashboard-data artifact, repository revision, and action commit. Publish is latest-wins on `main`: a newer publish cancels an older pending or running publish so obsolete renders do not overwrite newer collection results. The publish workflow can also be run manually against the current template revision.

## Configuration

Edit [config.yaml](config.yaml) to choose which repositories are tracked.

```yaml
max_repos: 50

include_only:
  # - owner/repo-name

include:
  # - owner/important-repo

exclude:
  # - owner/noisy-repo

include_others: true
include_new: false
include_private: true

# Optional: disable Reponomics-managed local docs updates.
allow_docs_sync: true
```

If `include_only` is non-empty, Reponomics tracks exactly those repositories and ignores the automatic pool.

Reponomics may update the managed local documentation namespace at `docs/reponomics/` before collection after action upgrades. It writes only that namespace, commits with `[skip ci]`, and treats missing write permission as advisory. Set `allow_docs_sync: false` before editing `docs/reponomics/` yourself.

### Token Scope And Repository Owners

Repository entries use full `owner/repo` names because a dashboard can be configured against repositories owned by users or organizations. The token you choose still controls which owners can actually be collected.

Fine-grained personal access tokens are scoped to one GitHub resource owner. If your dashboard only tracks repositories under one user or one organization, a fine-grained token with repository `Administration: read` is the preferred path.

This template currently supports one collection credential. If one dashboard needs to track repositories under multiple users or organizations, the fine-grained token flow is not the right fit for the current single-token setup. Use a classic PAT with `repo` scope where the relevant organizations allow it. Classic PATs are broader and can access repositories your GitHub account can access, so use this fallback only when the dashboard really needs to span owners.

## Storage And Output

The canonical store is the `dashboard-data` Actions artifact.

- `strong` and `casual` store encrypted retained data as `dashboard-data.enc`.
- `plain` stores retained CSV files directly in the artifact and is rejected in public repositories.
- The dashboard HTML is generated during `publish`; it is deployed through GitHub Pages Actions artifacts only when hosted dashboard publication is enabled, and otherwise uploaded as a downloadable workflow artifact.
- The automatic publish path consumes the `reponomics-collect-provenance` artifact from the triggering collect run, then restores that run's `dashboard-data` artifact and checks out the recorded repository SHA and action SHA before rendering.
- Setup commits a static README. Metric README output is committed only when setup enables `generate_readme` in a private repository.
- Managed local documentation, when enabled, is committed only under `docs/reponomics/`.

For encrypted dashboards, unlock the hosted Pages dashboard with the same dashboard key stored in `DASHBOARD_SECRET_DO_NOT_REPLACE`. After unlock, the dashboard can export a canonical CSV ZIP in the browser. The export path downloads an encrypted asset, decrypts it locally, verifies SHA-256 digests, and does not upload plaintext CSV back to GitHub.

To view a dashboard offline, open a successful **Publish Reponomics dashboard** workflow run and download the dashboard artifact before it expires. Extract the artifact and open `index.html`. Some browsers block local `file://` fetches; if export fails offline, serve the extracted artifact directory over local HTTP or use the hosted Pages dashboard.

More details are in [docs/README.md](docs/README.md).

Repository access is part of the dashboard security model. In personal private repositories, collaborators should be treated as trusted with the dashboard control plane, not merely as people who can read a report. See [Repository Access And Trust Boundary](docs/TRUST_BOUNDARY.md).

Common privacy, storage, export, and trust-boundary questions are answered in the [FAQ](docs/FAQ.md).

For release, dependency, vendored-asset, and generated-artifact verification, see [Provenance And Supply Chain Verification](docs/PROVENANCE.md).

## Scheduled Workflow Liveness

GitHub documents that scheduled workflows in public repositories may be disabled automatically after 60 days without repository activity, and inactive scheduled workflows are an operational risk for any dashboard repository. Setup enables a monthly keepalive workflow across repository visibility modes. It uses only the repository `GITHUB_TOKEN`, commits `.reponomics/keepalive.md`, and tries to create one persistent data safety reminder issue. This is a best-effort safeguard because GitHub does not precisely define the activity criteria. If scheduled workflows stop unexpectedly, download the latest `dashboard-data` artifact before it expires and re-enable workflows from the Actions tab.

## Incident Response And Outage Preservation

Ordinary collection outages are handled by artifact retention and active supersession rather than a separate preservation workflow. Collection uploads a successor `dashboard-data` artifact before older superseded artifacts are cleaned up. If collection fails, no successor is uploaded and no cleanup is attempted, so the previous unexpired artifact remains the recovery point.

`incident-reset` is a separate manual workflow for suspected dashboard-key exposure. For serious exposure, make the dashboard repository private and disable any published Pages dashboard before running it. Then set `DASHBOARD_NEXT_SECRET`, run **Actions -> Reset Reponomics dashboard incident history**, and enter all three confirmation strings. After the run succeeds, promote `DASHBOARD_NEXT_SECRET` into `DASHBOARD_SECRET_DO_NOT_REPLACE`, then delete `DASHBOARD_NEXT_SECRET`.

### Advanced: User-Owned GitHub App Collection Token

Advanced users can run collection with a user-owned GitHub App installation token instead of a PAT:

1. Create and install your own GitHub App (Reponomics does **not** provide or operate a shared collection app).
2. Grant the app repository `Administration: read` for collection endpoints.
3. Add `COLLECTION_APP_PRIVATE_KEY` as a repository secret.
4. Add `COLLECTION_APP_ID` as a repository variable (or secret).
5. Run setup with `use_github_app: true`.

In this mode, the generated collect workflow mints a short-lived installation token during the run and passes it to `reponomics-dashboard-action` with `use-github-app: true`.

## Runtime Requirements

Template repositories do not require local Python for normal use. Collection, publish, setup, and rotation run in GitHub Actions.

If you run workflows on self-hosted runners, provide:

- Python `3.11+`
- GitHub CLI (`gh`) for setup token validation

For maintainers working in `reponomics-dashboard-dev`, local tooling supports Python `3.11+` and maintainer CI validates Python `3.11` and `3.12`.
Dependency lock maintenance and automation are documented in [docs/MAINTAINER_DEPENDENCY_PROTOCOL.md](docs/MAINTAINER_DEPENDENCY_PROTOCOL.md).
