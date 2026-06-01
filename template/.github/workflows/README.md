# Template Workflows

> [!WARNING]
> Pre-release placeholder.
> The generated workflow surface is public for testing, but it is not final
> product guidance.

The workflows in this directory are generated from
`reponomics/reponomics-dashboard-dev` and delegate runtime behavior to
`reponomics/reponomics-dashboard-action`.

- `setup.yml` prepares a generated dashboard repository.
- `collect.yml` runs scheduled collection. Its manual dispatch also includes
  `incident-reset`, a destructive rekey-and-purge path for compromised encrypted
  history.
- `incident-sentinel.yml` is the non-destructive data-loss prevention backstop.
  When collection fails, it preserves the latest unexpired `dashboard-data`
  artifact with a long retention period.
- `keepalive.yml` performs scheduler liveness maintenance.
- `publish.yml` renders configured dashboard outputs.
- `rotate-key.yml` rotates encrypted dashboard state to a new secret.

Managed runtime documentation is written under `docs/reponomics/` when
docs sync runs and remains the preferred location for behavior details.
