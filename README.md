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
2. Add a repository secret named `TRAFFIC_TOKEN`.
   A classic token with `repo` scope is the most reliable choice for private
   repositories and hosted GitHub Pages setup. Public-only collection can use a
   narrower token if it can read the target repositories' traffic APIs.
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

Setup enables the collection workflow and leaves publish disabled unless
`publish_dashboard` is enabled during setup. It does not collect traffic
immediately. Collection runs twice daily on `main`; publication runs after
successful collection and can also be run manually.

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

## Storage And Output

The canonical store is the `traffic-data` Actions artifact.

- `strong` and `casual` store encrypted retained data as `traffic-data.enc`.
- `plain` stores retained CSV files directly in the artifact and is rejected in
  public repositories.
- The dashboard HTML is generated during `publish` and deployed through GitHub
  Pages Actions artifacts.
- README output is committed only when setup enables `commit-outputs`.

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
- GitHub CLI (`gh`) for setup workflow repository-configuration calls

For maintainers working in `reponomics-dashboard-dev`, local tooling supports
Python `3.11+` and maintainer CI validates Python `3.11` and `3.12`.
