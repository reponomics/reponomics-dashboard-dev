# Maintainer Dependency Update Protocol

This repository uses hash-pinned lock files and a two-lane update model:

- `requirements.txt` and `requirements-dev.txt` are the source constraints.
- `requirements.lock` and `requirements-dev.lock` are the exact install set used by CI.

## Why This Exists

`pip-compile` can resolve newer transitive versions when run against a fresh output file. Without controls, CI can fail on unrelated PRs because an upstream package was published between runs.

To avoid that drift, lock validation is deterministic and does not auto-upgrade.

## Maintainer Commands

- `make lock-requirements`
  - Rebuild lock files from current pins without upgrades (`--no-upgrade`).
  - Use after changing `requirements*.txt` when you want to preserve existing resolved versions.
- `make upgrade-requirements`
  - Intentionally refresh lock files to latest resolvable versions (`--upgrade`).
- `make validate-requirement-locks`
  - Confirms lock files are reproducible from current constraints and hash-installable.

## Automation

- Dependabot is enabled via `.github/dependabot.yml` for:
  - Python (`package-ecosystem: pip`)
  - GitHub Actions (`package-ecosystem: github-actions`)
- `DEV / Refresh Dependency Locks` runs weekly (and on manual dispatch):
  - runs `make upgrade-requirements`
  - validates with `make validate-requirement-locks`
  - opens or updates a PR `automation/dependency-lock-refresh`

This separation keeps normal feature/release PRs stable while still refreshing dependency locks on a reliable cadence.

## Incident Playbook

If CI fails on `validate-requirement-locks` due lock drift:

1. Run `make upgrade-requirements`.
2. Commit updated lock files.
3. Re-run CI.

If automation cannot open PRs (for example, restricted token permissions), run the refresh workflow manually with `workflow_dispatch` and push the resulting lock update from a maintainer branch.
