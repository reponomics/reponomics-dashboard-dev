# Encrypted Payload Size And Side Channels

Status: current for action `v0.16.0`.

Encrypted hosted dashboards protect dashboard contents from viewers without
`DASHBOARD_SECRET_DO_NOT_REPLACE`, but they do not make the publication opaque.

## Current Surface

The dashboard renderer lives in `reponomics-dashboard-action`. In `strong` and
`casual`, `publish` renders encrypted dashboard HTML. When hosted publication
is enabled, that output is deployed as a GitHub Pages artifact. Otherwise, it
remains a downloadable workflow artifact. The generated repository does not
commit the dashboard HTML.

The public hosted surface can still reveal:

- that a dashboard exists
- publication timing
- encrypted payload size
- payload size changes over time
- static shell changes across action releases

This is metadata leakage, not plaintext disclosure. With a strong dashboard key,
AES-GCM prevents content inspection, but payload length can still suggest rough
dashboard scale.

## Size Drivers

Payload size is influenced by:

- number of tracked repositories
- retained day count
- repository name length
- top path and referrer row count
- repeated frontend convenience structures
- repository growth series
- encrypted CSV export asset size

The canonical CSV export ZIP is encrypted separately for browser-local export,
so export support increases Pages artifact size.

## User-Facing Claim

The defensible claim is:

```text
Encrypted dashboards protect dashboard data contents from people who do not
have the dashboard key. They do not hide the existence of the site, update
timing, artifact size, or the fact that the repository is using Reponomics.
```

`casual` mode weakens the content-protection claim because weak or shared
secrets can be guessed offline from the encrypted payload.

## Mitigations

Mitigations belong in `reponomics-dashboard-action`, not this template repo.
Reasonable future action-side work includes:

- compact payload schemas that avoid repeated repo/path strings
- compression before encryption if browser compatibility is acceptable
- bucket padding before encryption to reduce precise size leakage
- externalized or chunked encrypted payload assets inside the Pages artifact
- clear docs that avoid overstating what encrypted Pages hides

Because dashboard files are deployed as Pages artifacts rather than committed
to git, `.gitattributes` diff handling is no longer a primary mitigation for
the generated template.

## Verification Posture

Security-focused users can still narrow trust by reviewing a specific action
release, pinning workflows to an exact tag or commit SHA, and inspecting the
release provenance. That does not remove the need to trust the action code, but
it makes the trust boundary explicit and auditable.
