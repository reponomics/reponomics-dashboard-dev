# Workflow Inventory

This directory contains maintainer workflows for `reponomics-dashboard-dev`. Template-consumer workflows live under `template/.github/workflows/` and are generated into the published template repository.

## Workflows

- [`dev-ci.yml`](dev-ci.yml): Primary maintainer CI for pull requests and `main`. Runs quality gates, template smoke checks, and template consumer e2e checks.

- [`dev-osv-scanner.yml`](dev-osv-scanner.yml): Runs OSV-Scanner and uploads SARIF results to GitHub code scanning on PRs, pushes, schedule, and manual dispatch.

- [`dev-release-please.yml`](dev-release-please.yml): Drives Release Please for dashboard-dev. Creates/updates release PRs and publishes releases, then dispatches downstream automation when a release is cut.

- [`dev-scorecard.yml`](dev-scorecard.yml): Runs OpenSSF Scorecard and publishes SARIF/results for supply-chain posture visibility and badge support.

- [`dev-semantic-pr.yml`](dev-semantic-pr.yml): Enforces semantic pull request titles on `pull_request_target` events so release automation receives consistent commit semantics.

- [`dev-sync-action-release.yml`](dev-sync-action-release.yml): Receives action-release dispatches (or manual input), syncs the accepted action release metadata/refs, verifies them, and opens or updates the automation PR in dashboard-dev.

- [`dev-template-release.yml`](dev-template-release.yml): On dashboard-dev release (or manual run), builds the generated template output and publishes it to the template repository.

## Conventions

Imported actions should remain pinned by full commit SHA with version comments. Workflow-level permissions stay minimal, with elevated permissions scoped only to jobs that need them.
