# Launch Readiness Checklist

Status: **Product-ready; generated-repository cutover pending**

## Core Product

- [x] Artifact-backed CSV storage pipeline (bootstrap, merge, trim)
- [x] GitHub API collection (views, clones, referrers, paths, stars, watchers, forks)
- [x] Cross-run artifact restore with retry logic
- [x] Deduplication and 90-day retention trim
- [x] Static HTML dashboard with Chart.js charts
- [x] Opt-in encrypted Pages mode
- [x] README snapshot generation
- [x] README SVG chart assets
- [x] Shared data-loading path (README and dashboard always agree)
- [x] First-run bootstrap (clean start with no prior artifact)
- [x] Second-run continuity (prior history preserved via artifacts)

## Workflow

- [x] GitHub Actions setup workflow and generated collection workflow (`collect.yml`)
- [x] Twice-daily default schedule (6 AM / 6 PM UTC)
- [x] Manual trigger support (`workflow_dispatch`)
- [x] Token validation and error handling
- [x] Auto-commit of rendered outputs only
- [x] `[skip ci]` on auto-commits to prevent loops

## Onboarding

- [x] Value-first README (leads with outcome, not implementation)
- [x] Guided setup workflow with privacy choices
- [x] Single token requirement (`TRAFFIC_TOKEN` with `repo` scope)
- [x] Zero-config repo discovery by default
- [x] Optional config overrides (`config.yaml` with repo priority + exclusion)
- [x] Direct link to token creation page
- [x] Public and private usage documented

## Documentation

- [x] Main README with quick setup
- [x] Advanced docs (`docs/README.md`)
- [x] Artifact storage behavior explained
- [x] Retention window documented
- [x] Local dashboard viewing instructions
- [x] Schedule customization guide
- [x] Encrypted Pages mode guide
- [x] Troubleshooting section
- [x] Upgrade path notes (DB promotion, extended retention)
- [x] CSV schema reference
- [x] ADR for encrypted Pages threat model

## Testing

- [x] Pipeline tests (21 tests)
- [x] Collection tests (32 tests)
- [x] Renderer tests (35 tests)
- [x] Cross-renderer agreement test (totals match)
- [x] Empty-data graceful handling
- [x] Makefile `test` target

## Template Hygiene

- [x] No database credentials required
- [x] No third-party service dependencies
- [x] `data/` directory git-ignored
- [x] Clean `.gitignore`
- [x] No leftover internal scaffolding in user-facing paths
- [x] Generated outputs (README, dashboard) are the only committed data

## Generated Repository Cutover

- [x] ADR accepts generated template and demo repositories
- [x] Template manifest defines the shipped user surface
- [x] Generated-template tests reject maintainer-only files
- [x] Demo build renders from deterministic mock CSV data
- [x] Demo collection workflow remains disabled
- [x] Publish script checks expected target repository names
- [ ] Runtime action repository model accepted for v1
- [ ] Runtime action packages collect and rotate-key modes
- [ ] Generic encrypted artifact action explicitly deferred beyond v1
- [ ] Product work freeze announced and limited to migration/release-safety work
- [x] Shadow dev, runtime action, template, and demo repositories provisioned privately
- [x] Shadow demo repository exists at the exact name `reponomics-dashboard-demo`
- [ ] Shadow dev repository default branch and remote naming finalized
- [ ] Shadow runtime action release/tagging policy confirmed
- [ ] Shadow template repository settings and branch protection confirmed
- [ ] Shadow demo repository secrets and Pages settings confirmed
- [ ] Staging consumer created from the generated template and validated across
  setup plus a second collection run
- [ ] Final migration sync completed from the existing repository
- [ ] Switch/no-switch decision recorded after shadow validation
- [ ] Transitional branch-model references retired or marked historical
