# Template Workflows

> [!WARNING]
> Pre-release placeholder workflow inventory.

These workflows are intentionally minimal wrappers around the [Reponomics Dashboard action](https://github.com/reponomics/reponomics-dashboard-actiob).

- `setup.yml`: bootstraps repository configuration, enables managed workflows, and writes initial setup state.
- `collect.yml`: scheduled/manual data collection, data encryption, and retained artifact update.
- `publish.yml`: renders rich HTML analytics dashboard in encrypted form to GitHub Pages, and optionally a simpler markdown dashboard to the repository's README.
- `rotate-key.yml`: rotates the encryption secret for encrypted data in case of exposure, changes in your trust boundary, or loss of access to the secret.
- `incident-sentinel.yml`: attempts to prevent existing data from expiring in case of unexpected outage or failure of the collection workflow.
- `keepalive.yml`: periodic activity keepalive to reduce schedule disablement risk.

Before running setup, all other workflows are guarded and are will simply write a summary telling users to run setup first.
