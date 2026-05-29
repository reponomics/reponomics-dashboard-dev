# Reponomics Dashboard Documentation

The Reponomics Dashboard is a GitHub-native repository traffic and growth dashboard. It collects views, clones, top referrers, popular paths, and repository growth counters, then renders static dashboard output during the `publish` workflow.

This generated repository is intentionally thin. The workflows call `reponomics/reponomics-dashboard-action@v0.12.1`, which owns collection, artifact restore/upload, schema migration, encryption, README rendering, dashboard rendering, CSV export packaging, and dashboard key rotation.

Template repositories do not require local Python for normal use. Workflows run in GitHub Actions and delegate runtime behavior to `reponomics/reponomics-dashboard-action`.

If a repository uses self-hosted runners, runner images should provide Python `3.11+` and GitHub CLI (`gh`) for setup token validation.

Maintainer CI for `reponomics-dashboard-dev` validates Python `3.11` and `3.12`.

## Repository Model

Your repository owns:

- `config.yaml`
- repository secrets
- workflow schedule and permissions
- the pinned action version
- retained `dashboard-data` workflow artifacts
- static post-setup README output
- optional committed metric README output when `generate_readme` is enabled during setup in a private repository

Your repository does not store any collected data in git. The dashboard HTML is rendered during `publish` and, for encrypted hosted dashboards, deployed as a GitHub Pages artifact.

Repository access is part of the dashboard security model. In personal private repositories, collaborators should be treated as trusted with the dashboard control plane, not merely as people who can read a report. See [Repository Access And Trust Boundary](TRUST_BOUNDARY.md).

Common privacy, storage, export, and trust-boundary questions are answered in the [FAQ](FAQ.md).

`COLLECTION_TOKEN` is only for repository data collection, including GitHub traffic data. Create it as a [fine-grained personal access token](https://github.com/settings/personal-access-tokens/new?name=COLLECTION_TOKEN&description=Read%20repository%20data%20for%20Reponomics%20Dashboard&expires_in=366&administration=read), choose the owner whose repositories should be collected, and keep the prefilled repository permission `Administration: read`. Choose **All repositories** for broad automatic discovery, or **Only selected repositories** if you want to limit collection to specific repositories. If you choose selected repositories, keep `config.yaml` within that token's repository access. The setup workflow uses the repository-scoped `GITHUB_TOKEN` to commit workflow enablement changes, so the collection token does not need repository, Pages, or Administration write permissions. Ideally, we will have one, limited-scope token responsible for any queries outside of the dashboard repo, and all other operations will be done by the repo's own `GITHUB_TOKEN`. This minimizes the scope of the collection token, which for many users will have access to lots of repositories.

This template currently supports one collection credential. Fine-grained personal access tokens are scoped to one GitHub resource owner. If one dashboard needs to track repositories under multiple users or organizations, the fine-grained token flow is not the right fit for the current single-token setup. Use a classic PAT with `repo` scope where the relevant organizations allow it. Classic PATs are broader and can access repositories your GitHub account can access.

## Configuration

`config.yaml` is the active configuration for this repository. It is user-owned: collection and publication runs read it, but do not silently rewrite it.

`config.example.yaml` shows the supported configuration shape. Missing optional keys use runtime defaults; explicit keys in `config.yaml` are treated as your choices.

## Privacy Modes

`privacy-mode` is the disclosure control passed to the action.

| Mode | Retained artifact | Hosted dashboard | Secret requirement | Intended use |
| --- | --- | --- | --- | --- |
| `strong` | encrypted `dashboard-data.enc` | encrypted Pages artifact | generated high-entropy `DASHBOARD_SECRET_DO_NOT_REPLACE` | default for public or sensitive dashboards |
| `casual` | encrypted `dashboard-data.enc` | encrypted Pages artifact | any non-empty `DASHBOARD_SECRET_DO_NOT_REPLACE` | low-sensitivity sharing where accidental discovery is the concern |
| `plain` | plaintext retained CSV files | disabled | none | private repositories that use GitHub repo/artifact access as the boundary |

`plain` is rejected in public repositories. Public repositories can use `strong` or `casual`, but README dashboard generation is rejected there so repository metrics are not committed to public git history.

> [!NOTE]
> We chose the deliberately outlandish name `DASHBOARD_SECRET_DO_NOT_REPLACE` precisely because there is no other way in the Action > Secrets UI to convey the message to the user that if they want to rotate the key, they should not do so by simply replacing that value, which seems like a tempting mistake.

## Storage

The canonical data store is the `dashboard-data` GitHub Actions artifact.

- `collect` restores the prior artifact, collects current GitHub data, merges and trims retained CSV history, then uploads a new `dashboard-data` artifact.
- `publish` restores the retained artifact, renders dashboard output, optionally renders private-repository metric README output, and deploys an encrypted Pages artifact for `strong` and `casual`.
- `rotate-key` restores encrypted retained state, decrypts with `DASHBOARD_SECRET_DO_NOT_REPLACE`, re-encrypts with `DASHBOARD_NEXT_SECRET`, and publishes rotated encrypted outputs.
- `keepalive` runs monthly, updates `.reponomics/keepalive.md`, and tries to create a persistent data safety reminder issue so scheduled collection is less likely to be silently disabled.

Git history is used for configuration, workflow shells, the static setup README, and optional private-repository metric README output. It is not the analytics database.

The template keeps GitHub Actions artifact retention at the default 90 days, which works across public repositories and default GitHub Actions settings.

## Scheduled Workflow Liveness

GitHub documents that scheduled workflows in public repositories may be disabled automatically after 60 days without repository activity, and inactive scheduled workflows are an operational risk for any dashboard repository. The generated repository enables a monthly keepalive workflow across repository visibility modes. It uses only the repository `GITHUB_TOKEN`, commits `.reponomics/keepalive.md`, and tries to create one persistent data safety reminder issue. This is a best-effort safeguard because GitHub does not precisely define the activity criteria, and GitHub can still change platform behavior. If scheduled workflows stop unexpectedly, download the latest `dashboard-data` artifact before it expires, then re-enable workflows from the Actions tab.

## CSV Export

Encrypted hosted dashboards include an `Export CSV` control after unlock. The browser downloads an encrypted export asset, decrypts it locally with the dashboard key, verifies ciphertext and plaintext SHA-256 digests, and downloads a canonical ZIP of retained CSV files. Plaintext CSV is not uploaded back to GitHub during export.

For `plain`, download the `dashboard-data` workflow artifact directly.

## Offline Viewing

The generated dashboard is not committed to this repository. To view an encrypted dashboard offline, open a successful **Publish Reponomics dashboard** workflow run and download the GitHub Pages artifact before it expires. Extract the artifact and open `index.html` with the same dashboard key that unlocks the hosted Pages dashboard.

Some browsers block local `file://` fetches used by CSV export. If export fails offline, serve the extracted artifact directory over local HTTP or use the hosted Pages dashboard.

## Key Rotation

1. Generate and save a new dashboard key.
2. Add it as `DASHBOARD_NEXT_SECRET`.
3. Run **Actions -> Rotate Reponomics dashboard key -> Run workflow**.
4. Confirm the dashboard opens with the new key.
5. Replace `DASHBOARD_SECRET_DO_NOT_REPLACE` with the new key (this a rare instance in which you are allowed to disobey the instructions in the secret's name).
6. Delete `DASHBOARD_NEXT_SECRET`.

Normal collection refuses to run while `DASHBOARD_NEXT_SECRET` is set, so rotation cannot be left half-finished unnoticed.

## GitHub Pages

For a hosted encrypted dashboard, manually configure this repository's **Settings -> Pages** page so **Build and deployment -> Source** is **GitHub Actions**. The Reponomics publish workflow renders the dashboard shell and uploads it as a GitHub Pages artifact; retained dashboard data remains in the `dashboard-data` Actions artifact. The action verifies the existing Pages setting during deployment, but it does not enable Pages or change the publishing source. If GitHub suggests workflow templates while you are changing the setting, skip them.

> [!WARNING]
> Unless your GitHub plan provides Pages access controls, a GitHub Pages site is reachable on the internet even when the repository is private. Use `privacy-mode=strong` when the hosted dashboard must not disclose metrics to people without the dashboard key.
