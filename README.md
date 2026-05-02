# Reponomics Dashboard

Capture GitHub traffic before it disappears, keep the history in GitHub
Actions artifacts, and publish a lightweight README snapshot plus an optional
HTML dashboard.

Reponomics runs entirely inside your repository. There is no external service,
database, or account to connect.

## Quick Setup

1. Create a repository from this template.
2. Add a repository secret named `TRAFFIC_TOKEN`.
3. For encrypted dashboard or encrypted artifact mode, add
   `TRAFFIC_DASHBOARD_SECRET`.
4. Run **Actions -> Set up Reponomics dashboard -> Run workflow**.

The setup workflow asks for:

- README dashboard summary: `disabled` or `metrics_summary`
- GitHub Pages dashboard: `encrypted`, `public`, or `disabled`

The private default for public repositories is encrypted Pages plus encrypted
Actions artifacts. Choose public output only if you are comfortable publishing
the traffic data.

## Token

`TRAFFIC_TOKEN` is used to read GitHub traffic and repository metadata. A
classic personal access token with `repo` scope is the most reliable option
when you want to include private repositories. If you only care about public
repositories, `public_repo` may be sufficient.

Create a token from your GitHub user settings, then save it in this repository
under **Settings -> Secrets and variables -> Actions**.

## Dashboard Key

Encrypted mode uses `TRAFFIC_DASHBOARD_SECRET` to encrypt the dashboard payload
and, when needed, the retained traffic artifact. Generate a long random value
with a password manager and store it somewhere private.

See [Secure Dashboard Key Generation](docs/SECURE_DASHBOARD_KEY.md) for
non-CLI options and rotation guidance.

## Configuration

Edit [config.yaml](config.yaml) to choose which repositories are tracked.

```yaml
max_repos: 50

include:
  - owner/important-repo

exclude:
  - owner/noisy-repo

include_others: true
include_new: false
include_private: true
```

If `include_only` is non-empty, Reponomics tracks exactly those repositories
and ignores the automatic pool.

## After Setup

Setup enables `.github/workflows/collect.yml`, runs the first collection, and
replaces this README with the selected dashboard output. The collection
workflow then runs twice daily on `main`.

For hosted Pages, set **Settings -> Pages -> Source** to **Deploy from a
branch**, choose branch `main`, folder `/docs`, then save.

More details are in [docs/README.md](docs/README.md).

