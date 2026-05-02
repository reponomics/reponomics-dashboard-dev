# ADR 0001: Encrypted Pages Mode

- Status: Accepted
- Date: 2026-04-09

## Context

Users wanted a stable dashboard URL that non-power users could open on desktop
or mobile without cloning the repository. The existing options covered two
extremes well:

- public GitHub Pages with plaintext metrics
- local-only viewing via the standalone HTML artifact

What was missing was a middle path for users who wanted a public Pages URL that
did **not** immediately expose their traffic numbers to outsiders who happened
to learn the URL. This became especially important for public template
repositories, where GitHub Free does not provide private-repository Pages and
workflow artifacts are not a confidentiality boundary.

This request came with a deliberately narrow threat model:

- people with the dashboard key are allowed to see the metrics
- the adversary can access the public repository, public Pages URL, or public
  workflow artifacts
- the adversary does not have `TRAFFIC_DASHBOARD_SECRET`
- the goal is to deter casual or low-skill snooping, not to provide
  enterprise-grade access control

## Decision

Add an opt-in encrypted Pages mode controlled by:

- `DASHBOARD_ACCESS_MODE=encrypted`
- `TRAFFIC_DASHBOARD_SECRET=<generated dashboard key>`

When enabled:

1. The renderer still builds the canonical dashboard payload from normalized
   CSV data.
2. The workflow encrypts that payload at render time using the dashboard key.
3. `docs/index.html` is replaced with a single-page shell that contains:
   - the encrypted payload
   - PBKDF2 parameters and AES-GCM metadata
   - a dashboard key prompt
   - client-side decryption logic using Web Crypto
4. When a public repository is not fully public, the workflow also encrypts the
   retained Actions data artifact before upload.

The public page must never contain:

- the dashboard key
- the plaintext dashboard payload

## Rationale

This approach fits the stated product constraints better than the alternatives:

- A fake login screen over plaintext data is security theater.
- A separate hosted auth service adds setup, maintenance, and product
  complexity that conflicts with the template-first happy path.
- GitHub Pages access control is not generally available for private repos
  unless the user is on GitHub Enterprise Cloud.
- Standalone artifacts remain the best no-public-URL path, but they do not
  provide a stable link for mobile or non-technical viewers.

Using build-time encryption plus client-side decryption gives the repo a stable
Pages URL while still keeping plaintext metrics out of the public response.

## Threat Model

Encrypted Pages mode is only intended to protect against:

- outsiders who discover the Pages URL
- people who can read a public repository or download public workflow artifacts
  but do not have the dashboard key
- casual or low-skill viewers without the key

It is **not** intended to protect against:

- anyone who can read repository secrets
- anyone who has the dashboard key
- anyone who can see a public README snapshot or public Pages dashboard because
  the user explicitly enabled public output
- a determined attacker willing to guess a weak dashboard key offline
- scenarios that require real authentication, revocation, auditing, or
  per-user authorization

## Consequences

- README metrics must be disabled in public encrypted setups, or the README
  itself becomes the leak.
- Dashboard key strength matters because the encrypted page and encrypted
  artifact can be downloaded and attacked offline.
- Rotating the key requires updating `TRAFFIC_DASHBOARD_SECRET` and rerunning
  setup.
- The standalone artifact remains the preferred option when the user wants no
  public URL at all.
- The renderer now carries a little more complexity, but the happy path stays
  simple because the mode is strictly opt-in.

## Notes On Secret Storage

For this repo, the dashboard key must come from a GitHub Actions secret named
`TRAFFIC_DASHBOARD_SECRET`. The user must also store the key outside GitHub,
usually in a password manager. The important invariant is that the key never
ships in a public output or workflow log.
