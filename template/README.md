# Reponomics Dashboard Template

This documentation is intentionally provisional.

Repository context:

- If you are in [`reponomics/reponomics-dashboard`](https://github.com/reponomics/reponomics-dashboard), this repository is a published generated artifact from [`reponomics/reponomics-dashboard-dev`](https://github.com/reponomics/reponomics-dashboard-dev).
- If you are in a repository created from this template, your repository is consumer-owned runtime configuration and workflow state.

> [!WARNING]
> Not intended for public production use yet. Behavior, interfaces, and documentation may change without notice before `v1`.

## Source Repositories

- Template generation source: [`reponomics/reponomics-dashboard-dev`](https://github.com/reponomics/reponomics-dashboard-dev)
- Runtime action: [`reponomics/reponomics-dashboard-action`](https://github.com/reponomics/reponomics-dashboard-action)

Collection, publish, encryption, rotation, and docs-sync behavior are implemented by the action and consumed by generated workflows.

## GitHub App Installations

- If you are in `reponomics/reponomics-dashboard`, a maintainer GitHub App installation may exist to support upstream publication automation.
- If you create a repository from this template, GitHub App installations are not inherited as repository content.
- Reponomics does not automatically gain access to repositories created from this template. Any app installation in a copied repository is controlled by that repository owner.

## Contribution Policy For This Repository

This repository does not accept direct pull requests for feature or runtime changes. If you need a change to the template or action behavior:

- Open an issue in `reponomics-dashboard-dev` for template, workflow, or documentation generation behavior.
- Open an issue in `reponomics-dashboard-action` for runtime/action behavior.

See [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md), and [SECURITY.md](SECURITY.md).

## Placeholder Docs

- [Documentation Index](docs/README.md)
- [Privacy Configuration Matrix](docs/PRIVACY_CONFIGURATION_MATRIX.md)
- [FAQ](docs/FAQ.md)
- [Trust Boundary](docs/TRUST_BOUNDARY.md)
- [Secure Dashboard Key Generation](docs/SECURE_DASHBOARD_KEY.md)
- [Provenance And Supply Chain Verification](docs/PROVENANCE.md)
