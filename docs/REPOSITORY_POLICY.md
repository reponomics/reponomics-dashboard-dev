# Repository Policy

This project uses generated repositories instead of long-lived release
branches.

## Source Of Truth

Human development happens in `reponomics-dashboard-dev`. That
repository owns:

- implementation code
- tests and maintainer CI
- `template-manifest.yml`
- deterministic demo data generation
- generated-output verification
- release automation

## Generated Artifacts

`reponomics-dashboard` is the shipped template artifact. It should be
generated from the dev repository and should contain only the files listed in
`template-manifest.yml`.

`reponomics-action` is the versioned runtime artifact. It should own
collection, artifact restore/upload, schema migration, encryption, README
rendering, HTML dashboard rendering, and dashboard key rotation. The generated
template should call a pinned action version instead of vendoring runtime
internals into every user repository.

`reponomics-dashboard-demo` is the generated demo artifact. It should
be built from the same template output, seeded with deterministic mock data, and
rendered in encrypted Pages mode.

## Change Policy

Default rule:

1. change source in the dev repository
2. run tests and generated-output checks
3. publish the generated template artifact
4. publish or refresh the generated demo artifact

Direct edits to generated repositories are emergency-only. Any emergency edit
must be backported to the dev repository before the next generated release, or
it will be overwritten.

During the pre-public shadow migration, the existing repository may remain the
temporary source of truth until the separate dev, template, and demo
repositories prove stable. While migration is the main priority, pause product
feature work in the existing repository and allow only migration,
release-safety, verification, and necessary documentation changes. Make a
deliberate switch/no-switch decision from the validation results before
unfreezing product work.

A generic encrypted artifact store action is a possible future extraction, but
it is not a v1 launch requirement. Keep that capability inside the traffic
runtime action until the dashboard product is stable.

Generated publishes must also pass the target-repository safety check in
`scripts/publish_generated_repo.py`. A publish command should fail rather than
force-update a remote whose repository name does not match the intended
template or demo target.

## Edit Location Policy

- Demo seed data is edited in `scripts/generate_demo_data.py`, not in
  generated CSV files.
- The shipped collection workflow is edited as
  `.github/workflows/collect.yml.disabled`, not as generated `collect.yml`.
- Setup and key-rotation workflows are edited in `.github/workflows/setup.yml`
  and `.github/workflows/rotate-key.yml`.
- Dashboard and README UI are edited in the renderers, then reviewed through
  `dist/demo/`.
- Runtime action behavior is edited and tested in the runtime source, then
  released through action tags.
- Template membership is edited in `template-manifest.yml`.
- Runtime Make targets that users should receive live in `Makefile`.
- Maintainer-only targets live in `maintainer.mk`.

## Verification Policy

The minimum local release check is:

```bash
make verify
```

For a faster generated-output-only check:

```bash
make release-dry-run
```

The generated template must reject maintainer tests, dev requirements,
maintainer CI, internal docs, demo data, local artifacts, and release tooling.

## Workflow Policy

Workflow state is governed by
`docs/GENERATED_REPOSITORY_MODEL.md#workflow-activation-matrix`.

In short:

- only the dev repo should run maintainer CI
- the template repo should not run product workflows itself
- the demo repo should not run live collection
- live `Collect GitHub Traffic` belongs only in user-created repositories after
  setup enables `collect.yml`

## Repository Surface Policy

Repository feature, workflow, and security settings are governed by
`docs/GENERATED_REPOSITORY_MODEL.md#repository-surface-policy`.

Run this after provisioning a repo, after publishing generated repos for the
first time, or any time GitHub settings drift:

```bash
make enforce-repo-policy
```
