# FAQ

## Is This Repository The Development Source?

No. This repository is generated output intended for template users.

Development happens in:

- [`reponomics/reponomics-dashboard-dev`](https://github.com/reponomics/reponomics-dashboard-dev)
- [`reponomics/reponomics-dashboard-action`](https://github.com/reponomics/reponomics-dashboard-action)

## Where Is Dashboard Data Stored?

Retained data is stored in the `dashboard-data` GitHub Actions artifact. It is not stored as the canonical dataset in git history.

## Does `publish` Always Deploy GitHub Pages?

No. Hosted Pages deployment depends on setup/configuration and privacy mode. Downloadable dashboard artifacts remain available through workflow artifacts.

## Can I Disable Managed Docs Sync?

Yes. Set `allow_docs_sync: false` in `config.yaml` if you do not want the action to update `docs/reponomics/`.

## Can I Use `plain` Mode In Public Repositories?

No. `plain` is private-repository only.

## Where Should I Report Problems?

Use [SUPPORT.md](../SUPPORT.md) for routing.
