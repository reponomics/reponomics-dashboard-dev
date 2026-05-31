# Reponomics Dashboard Template Docs

This documentation set is pre-release placeholder content for two contexts:

- `reponomics/reponomics-dashboard` (the published template repository)
- repositories created from that template

It is intentionally user-facing and does not include maintainer ADRs or source-repo development protocols.

> [!WARNING]
> Not intended as final production guidance yet.

## Documents

- [Privacy Configuration Matrix](PRIVACY_CONFIGURATION_MATRIX.md)
- [FAQ](FAQ.md)
- [Trust Boundary](TRUST_BOUNDARY.md)
- [Secure Dashboard Key Generation](SECURE_DASHBOARD_KEY.md)
- [Provenance And Supply Chain Verification](PROVENANCE.md)

## Source Repositories

- Template generation source: [`reponomics/reponomics-dashboard-dev`](https://github.com/reponomics/reponomics-dashboard-dev)
- Runtime action source: [`reponomics/reponomics-dashboard-action`](https://github.com/reponomics/reponomics-dashboard-action)

## GitHub App Installation Boundary

Any GitHub App installed on `reponomics/reponomics-dashboard` does not imply installation on repositories created from the template. Installation/access decisions for copied repositories are owned by each repository owner.
