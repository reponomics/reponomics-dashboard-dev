# Reponomics Dashboard Documentation

Reponomics is a GitHub-native traffic dashboard. It collects views, clones,
top referrers, popular paths, and repository growth counters, then renders
static dashboard output during the `publish` workflow.

This generated repository is intentionally thin. The workflows call
`reponomics/reponomics-dashboard-action@v0.8.0`, which owns collection,
artifact restore/upload, schema migration, encryption, README rendering,
dashboard rendering, CSV export packaging, and dashboard key rotation.

Template repositories do not require local Python for normal use. Workflows run
in GitHub Actions and delegate runtime behavior to
`reponomics/reponomics-dashboard-action`.

If a repository uses self-hosted runners, runner images should provide Python
`3.11+` and GitHub CLI (`gh`) for setup token validation.

Maintainer CI for `reponomics-dashboard-dev` validates Python `3.11` and
`3.12`.

## Repository Model

Your repository owns:

- `config.yaml`
- repository secrets
- workflow schedule and permissions
- the pinned action version
- retained `traffic-data` workflow artifacts
- optional committed README output when `commit-outputs` is enabled

Your repository does not store retained traffic data in git. The dashboard HTML
is rendered during `publish` and, for encrypted hosted dashboards, deployed as
a GitHub Pages artifact.

`TRAFFIC_TOKEN` is only for reading repository traffic data. Create it as a
[fine-grained personal access token](https://github.com/settings/personal-access-tokens/new?name=Reponomics%20Traffic%20Token&description=Read%20repository%20traffic%20for%20Reponomics%20Dashboard&expires_in=366&administration=read),
choose the owner whose repositories should be collected, and keep the prefilled
repository permission `Administration: read`. Choose **All repositories** for
broad automatic discovery, or **Only selected repositories** if you want to
limit collection to specific repositories. If you choose selected repositories,
keep `config.yaml` within that token's repository access. The setup workflow
uses the repository-scoped `GITHUB_TOKEN` to commit workflow enablement changes,
so the traffic token does not need repository, Pages, or Administration write
permissions.

## Configuration

`config.yaml` is the active configuration for this repository. It is
user-owned: collection and publication runs read it, but do not silently rewrite
it.

`config.example.yaml` shows the supported configuration shape. Missing
optional keys use runtime defaults; explicit keys in `config.yaml` are treated
as your choices.

## Privacy Modes

`privacy-mode` is the disclosure control passed to the action.

| Mode | Retained artifact | Hosted dashboard | Secret requirement | Intended use |
| --- | --- | --- | --- | --- |
| `strong` | encrypted `traffic-data.enc` | encrypted Pages artifact | generated high-entropy `TRAFFIC_DASHBOARD_SECRET` | default for public or sensitive dashboards |
| `casual` | encrypted `traffic-data.enc` | encrypted Pages artifact | any non-empty `TRAFFIC_DASHBOARD_SECRET` | low-sensitivity sharing where accidental discovery is the concern |
| `plain` | plaintext retained CSV files | disabled | none | private repositories that use GitHub repo/artifact access as the boundary |

`plain` is rejected in public repositories. Public repositories can use
`strong` or `casual`, but README metrics are not committed there; public README
output is limited to a non-metric status block.

## Storage

The canonical data store is the `traffic-data` GitHub Actions artifact.

- `collect` restores the prior artifact, collects current GitHub data, merges
  and trims retained CSV history, then uploads a new `traffic-data` artifact.
- `publish` restores the retained artifact, renders README/dashboard output,
  and deploys an encrypted Pages artifact for `strong` and `casual`.
- `rotate-key` restores encrypted retained state, decrypts with
  `TRAFFIC_DASHBOARD_SECRET`, re-encrypts with
  `TRAFFIC_DASHBOARD_NEXT_SECRET`, and publishes rotated encrypted outputs.

Git history is used for configuration, workflow shells, and optional README
output. It is not the analytics database.

The template keeps GitHub Actions artifact retention at the default 90 days,
which works across public repositories and default GitHub Actions settings.

## CSV Export

Encrypted hosted dashboards include an `Export CSV` control after unlock. The
browser downloads an encrypted export asset, decrypts it locally with the
dashboard key, verifies ciphertext and plaintext SHA-256 digests, and downloads
a canonical ZIP of retained CSV files. Plaintext CSV is not uploaded back to
GitHub during export.

For `plain`, download the `traffic-data` workflow artifact directly.

## Offline Viewing

The generated dashboard is not committed to this repository. To view an
encrypted dashboard offline, open a successful **Publish Reponomics dashboard**
workflow run and download the GitHub Pages artifact before it expires. Extract
the artifact and open `index.html` with the same dashboard key that unlocks the
hosted Pages dashboard.

Some browsers block local `file://` fetches used by CSV export. If export fails
offline, serve the extracted artifact directory over local HTTP or use the
hosted Pages dashboard.

## Key Rotation

1. Generate and save a new dashboard key.
2. Add it as `TRAFFIC_DASHBOARD_NEXT_SECRET`.
3. Run **Actions -> Rotate Reponomics dashboard key -> Run workflow**.
4. Confirm the dashboard opens with the new key.
5. Replace `TRAFFIC_DASHBOARD_SECRET` with the new key.
6. Delete `TRAFFIC_DASHBOARD_NEXT_SECRET`.

Normal collection refuses to run while `TRAFFIC_DASHBOARD_NEXT_SECRET` is set,
so rotation cannot be left half-finished unnoticed.

## GitHub Pages

For a hosted encrypted dashboard, manually configure this repository's
**Settings -> Pages** page so **Build and deployment -> Source** is
**GitHub Actions**. The Reponomics publish workflow renders the dashboard shell
and uploads it as a GitHub Pages artifact; retained traffic data remains in the
`traffic-data` Actions artifact. The action verifies the existing Pages setting
during deployment, but it does not enable Pages or change the publishing source.
If GitHub suggests workflow templates while you are changing the setting, skip
them.

> [!WARNING]
> Unless your GitHub plan provides Pages access controls, a GitHub Pages site
> is reachable on the internet even when the repository is private. Use
> `privacy-mode=strong` when the hosted dashboard must not disclose metrics to
> people without the dashboard key.
