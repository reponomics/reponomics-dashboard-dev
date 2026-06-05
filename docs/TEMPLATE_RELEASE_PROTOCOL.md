# Template Release Protocol

Status: tentative maintainer protocol.

This document records the release cadence between `reponomics-dashboard-action`, `reponomics-dashboard-dev`, and the generated `reponomics-dashboard` template. It is operational guidance, not an ADR.

## Repository Roles

`reponomics-dashboard-action` owns runtime behavior: collection, artifact handling, encryption, rendering, managed docs sync, key rotation, incident reset, and compatibility of action modes.

`reponomics-dashboard-dev` owns acceptance of an action release into the generated template. It also owns generated workflow defaults, template docs, template release versions, and publication to `reponomics-dashboard`.

`reponomics-dashboard` is the generated template repository. It should be published from dashboard-dev releases, not edited directly except for emergency recovery.

## Cadence

An action release may open an action-sync PR in dashboard-dev. That PR updates `template-action-release.yml`, generated workflow action refs, provenance metadata, and action-version status text.

Merging an action-sync PR means dashboard-dev has accepted that action release for future template work. It does not by itself mean the generated template must be published immediately.

A dashboard-dev release is a separate maintainer decision. It is required when the accepted state should ship to new template users or to the generated template repository.

This separation gives maintainers a safety cushion: action releases can be accepted and tested in dashboard-dev without forcing a generated-template publication before the template surface is ready.

## When To Release Dashboard-Dev

Publish a dashboard-dev release when a change should reach the generated template. Common cases:

- generated workflow files, permissions, schedules, defaults, or setup behavior changed;
- user-facing template docs changed;
- managed docs bundled by the action changed and should be available to generated repositories;
- a newly accepted action release changes the workflow contract, generated docs, managed docs, incident response behavior, privacy behavior, or other template-visible behavior;
- the accepted action version contains a fix that new template repositories should receive by default.

Do not assume every action release requires an immediate dashboard-dev release. An action-only fix may be safe for existing users to adopt by changing their workflow action ref, while the template can wait for the next planned publication if no template-visible behavior changed.

## Semantic Versioning

Dashboard-dev and the generated template should use semantic versioning for template releases.

- Patch: template bug fixes, documentation corrections, accepted action fixes that should ship to new template users, managed-docs corrections, and non-breaking workflow hardening.
- Minor: new template capabilities, new generated workflows, new setup options, new user-visible docs/features, or non-breaking action capabilities that change the default generated-template experience.
- Major: breaking changes to setup, workflow contracts, configuration shape, privacy semantics, artifact expectations, or user migration requirements.

The action repository has its own semantic versioning stream. Dashboard-dev does not automatically mirror the action version number.

## Release Requests

Release Please controls dashboard-dev releases. When maintainers decide that the accepted state should publish, create a release-request commit or PR with an explicit `Release-As` trailer:

```text
chore(release): request dashboard-dev 0.5.2

Release-As: 0.5.2
```

Use the next dashboard-dev semantic version, not the action version. For example, accepting `reponomics-dashboard-action@v0.18.0` might request dashboard-dev `0.5.2` if the template change is a patch release.

The release request should state why the template should publish, for example:

```text
Publish the accepted v0.18.0 action release so new generated repositories get the incident-reset runtime baseline.
```

Release Please then opens the normal release PR. Merging that release PR cuts the dashboard-dev release, and the template publication workflow publishes `reponomics-dashboard` from that release source.

## Review Checklist

Before requesting a dashboard-dev release:

- verify `template-action-release.yml` points at the intended accepted action tag and commit;
- run or rely on passing dashboard-dev CI, including template smoke and template-consumer e2e when workflow behavior changed;
- confirm whether managed docs changed and need to ship;
- choose the dashboard-dev semantic version bump based on template impact;
- include `Release-As` only when publication is intentional.

If an action-sync PR is accepted but not released, leave the accepted action state in dashboard-dev and publish it with the next intentional dashboard-dev release.
