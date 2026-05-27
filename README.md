# Reponomics Dashboard

Reponomics preserves GitHub traffic data beyond GitHub's rolling traffic
window and turns it into a GitHub-native dashboard. A repository created from
this template collects views, clones, top referrers, popular paths, and
repository growth counters into retained GitHub Actions artifacts. The HTML
dashboard is rendered during the publish workflow and deployed as a GitHub Pages
artifact; traffic data is not committed to the repository.

The template is intentionally thin. Collection, artifact handling, schema
migration, encryption, dashboard rendering, CSV export, and key rotation are
owned by the versioned action:

```yaml
uses: reponomics/reponomics-dashboard-action@v0.8.0
```

## Setup

1. Create a repository from this template.
2. Create a token and add it as a repository secret named `TRAFFIC_TOKEN`.
   [Create a fine-grained personal access token](https://github.com/settings/personal-access-tokens/new?name=Reponomics%20Traffic%20Token&description=Read%20repository%20traffic%20for%20Reponomics%20Dashboard&expires_in=366&administration=read),
   choose the owner whose repositories should be collected, and keep the
   prefilled repository permission `Administration: read`. Choose **All
   repositories** for broad automatic discovery, or **Only selected
   repositories** if you want to limit collection to specific repositories. If
   you choose selected repositories, keep `config.yaml` within that token's
   repository access. If this dashboard must track repositories under multiple
   GitHub users or organizations, read
   [Token Scope And Repository Owners](#token-scope-and-repository-owners)
   before choosing a token. Do not grant Pages or Administration write
   permissions to this token for dashboard setup. Setup uses the workflow
   `GITHUB_TOKEN` to commit workflow enablement changes in this repository.
3. Choose a privacy mode:
   - `strong`: encrypted retained artifacts and encrypted hosted dashboard;
     requires a generated high-entropy `TRAFFIC_DASHBOARD_SECRET`.
   - `casual`: encrypted retained artifacts and encrypted hosted dashboard;
     accepts any non-empty `TRAFFIC_DASHBOARD_SECRET`, but is not intended to
     resist targeted offline guessing.
   - `plain`: plaintext retained CSV artifacts; private repositories only and
     no hosted Pages dashboard.
4. For `strong` or `casual`, add `TRAFFIC_DASHBOARD_SECRET` and store the same
   value somewhere private. See
   [Secure Dashboard Key Generation](docs/SECURE_DASHBOARD_KEY.md).
5. Run **Actions -> Set up Reponomics dashboard -> Run workflow**.
6. For a hosted encrypted dashboard, open this repository's
   **Settings -> Pages** page and set **Build and deployment -> Source** to
   **GitHub Actions**. If GitHub suggests workflow templates, skip them; the
   Reponomics publish workflow already deploys the Pages artifact.

Setup enables the collection workflow and leaves HTML dashboard generation
disabled unless `generate_html_dashboard` is enabled during setup. README
dashboard generation is disabled unless `generate_readme` is enabled during
setup. Setup does not collect traffic immediately. Collection runs twice daily
on `main`; dashboard generation runs after successful collection and can also
be run manually.

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
```

If `include_only` is non-empty, Reponomics tracks exactly those repositories
and ignores the automatic pool.

### Token Scope And Repository Owners

Repository entries use full `owner/repo` names because a dashboard can be
configured against repositories owned by users or organizations. The token you
choose still controls which owners can actually be collected.

Fine-grained personal access tokens are scoped to one GitHub resource owner. If
your dashboard only tracks repositories under one user or one organization, a
fine-grained token with repository `Administration: read` is the preferred path.

If one dashboard needs to track repositories under multiple users or
organizations, the fine-grained token flow is not the right fit for the current
single-token setup. Use a classic PAT with `repo` scope where the relevant
organizations allow it. Classic PATs are broader and can access repositories
your GitHub account can access, so use this fallback only when the dashboard
really needs to span owners.

## Storage And Output

The canonical store is the `traffic-data` Actions artifact.

- `strong` and `casual` store encrypted retained data as `traffic-data.enc`.
- `plain` stores retained CSV files directly in the artifact and is rejected in
  public repositories.
- The dashboard HTML is generated during `publish` and deployed through GitHub
  Pages Actions artifacts.
- README output is committed only when setup enables `generate_readme`.

For encrypted dashboards, unlock the hosted Pages dashboard with the same
dashboard key stored in `TRAFFIC_DASHBOARD_SECRET`. After unlock, the dashboard
can export a canonical CSV ZIP in the browser. The export path downloads an
encrypted asset, decrypts it locally, verifies SHA-256 digests, and does not
upload plaintext CSV back to GitHub.

To view a dashboard offline, open a successful **Publish Reponomics dashboard**
workflow run and download the GitHub Pages artifact before it expires. Extract
the artifact and open `index.html`. Some browsers block local `file://` fetches;
if export fails offline, serve the extracted artifact directory over local HTTP
or use the hosted Pages dashboard.

More details are in [docs/README.md](docs/README.md).

## Runtime Requirements

Template repositories do not require local Python for normal use. Collection,
publish, setup, and rotation run in GitHub Actions.

If you run workflows on self-hosted runners, provide:

- Python `3.11+`
- GitHub CLI (`gh`) for setup token validation

For maintainers working in `reponomics-dashboard-dev`, local tooling supports
Python `3.11+` and maintainer CI validates Python `3.11` and `3.12`.
