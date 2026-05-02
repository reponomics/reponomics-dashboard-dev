# Reponomics Privacy And Configuration Matrix

Version: 0.1 intended design

This document separates repository visibility from output disclosure.

- Repository visibility: who can read the repository.
- README dashboard: whether metrics are committed to `README.md`.
- Pages dashboard: whether `docs/index.html` is disabled, encrypted, or plain.
- Artifact mode: whether retained canonical CSV data is encrypted or plain.

Use `plain` to mean unencrypted. Do not use `public` as shorthand for
plaintext.

## Configuration Dimensions

Repository visibility:

- private or internal: repository read access is limited by GitHub permissions.
- public: repository content is visible to anyone.

README dashboard:

- disabled: README contains no metrics.
- enabled: README contains a non-interactive dashboard with rich metrics and
  SVG visualizations. This is not a second-class surface; it is a static
  dashboard optimized for GitHub README viewing.

Pages dashboard:

- disabled: no hosted dashboard surface.
- encrypted: dashboard payload is encrypted and unlocked client-side.
- plain: dashboard payload is written unencrypted.

Artifact mode:

- encrypted: retained canonical data is encrypted before upload.
- plain: retained canonical data is uploaded as CSV.

## Permutation Matrix

| Visibility | README | Pages | Artifact | Privacy boundary | Likely persona | UX framing |
|------------|--------|-------|----------|------------------|----------------|------------|
| private | disabled | disabled | encrypted | Data exists only in encrypted artifacts; repo readers see no metrics. | Security-first maintainer collecting history before deciding how to publish. | "Store only, maximum caution." |
| private | disabled | disabled | plain | Repo/artifact readers can access retained CSV; no committed metrics. | Solo maintainer who trusts private repo access controls. | "Store only inside the repo boundary." |
| private | enabled | disabled | encrypted | Repo readers see README metrics; retained CSV is encrypted. | Consultant or small team wanting GitHub-native private reporting. | "Private README dashboard." |
| private | enabled | disabled | plain | Repo/artifact readers see README and retained CSV. | Internal team using GitHub permissions as the privacy boundary. | "Internal analytics workspace." |
| private | disabled | encrypted | encrypted | Repo readers can open encrypted Pages only with key; retained data encrypted. | Maintainer who wants hosted UI but separate key sharing. | "Hosted dashboard with key boundary." |
| private | disabled | encrypted | plain | Repo/artifact readers can access CSV; dashboard still requires key. | Team trusting artifact access but limiting casual dashboard viewing. | "Encrypted UI, repo-bound data." |
| private | enabled | encrypted | encrypted | Repo readers see README metrics; Pages needs key; retained CSV encrypted. | Team dashboard with README summary and controlled hosted detail. | "Private README plus keyed dashboard." |
| private | enabled | encrypted | plain | Repo readers see README and CSV; Pages needs key. | Internal engineering org with repo access as data boundary. | "Internal README plus keyed UI." |
| private | disabled | plain | encrypted | Plain Pages output exposes dashboard wherever Pages is reachable; retained CSV encrypted. | Maintainer intentionally sharing hosted dashboard but not raw history. | "Hosted plain dashboard, protected retained data." |
| private | disabled | plain | plain | Plain Pages and retained CSV are unencrypted. | Low-sensitivity private project where convenience dominates. | "Convenience mode." |
| private | enabled | plain | encrypted | README and Pages disclose metrics; retained CSV encrypted. | Private repo with deliberately shared reporting outputs. | "Published surfaces, protected history." |
| private | enabled | plain | plain | README, Pages, and retained CSV are all repo/Pages-accessible. | Internal open-book metrics team. | "Everything visible inside chosen boundaries." |
| public | disabled | disabled | encrypted | Public repo shows no metrics; retained data encrypted. | Open-source maintainer collecting private history only. | "Open repo, private analytics store." |
| public | disabled | disabled | plain | Retained CSV may be accessible to anyone with artifact access; no committed metrics. | Rare/debug-only profile; usually avoid. | "Store only, but artifact data is unencrypted." |
| public | enabled | disabled | encrypted | README metrics are visible to anyone; retained CSV encrypted. | Open-source project sharing high-level traffic in README. | "Open README dashboard, protected history." |
| public | enabled | disabled | plain | README and retained CSV are unencrypted. | Project intentionally publishing traffic history. | "Open metrics archive." |
| public | disabled | encrypted | encrypted | Public repo has encrypted hosted dashboard; key holders see metrics. | Open-source maintainer sharing dashboard with collaborators only. | "Open repo, keyed dashboard." |
| public | disabled | encrypted | plain | Dashboard needs key, but retained CSV may be unencrypted. | Inconsistent privacy profile; usually avoid. | "Keyed UI, exposed retained data risk." |
| public | enabled | encrypted | encrypted | README metrics are open; detailed dashboard requires key; retained CSV encrypted. | Project sharing summary publicly and detail privately. | "Public summary, private detail." |
| public | enabled | encrypted | plain | README open; encrypted UI; retained CSV may disclose detail. | Usually avoid unless artifacts are intentionally disclosed. | "Mixed disclosure with artifact risk." |
| public | disabled | plain | encrypted | Hosted dashboard is open; retained CSV encrypted. | Project intentionally publishes dashboard but protects raw retained history. | "Open hosted dashboard, protected raw data." |
| public | disabled | plain | plain | Hosted dashboard and retained CSV are open/plain. | Fully transparent open-source metrics project. | "Open dashboard and open archive." |
| public | enabled | plain | encrypted | README and Pages are open; retained CSV encrypted. | Public project using metrics as social proof but protecting raw history. | "Open published metrics, protected archive." |
| public | enabled | plain | plain | README, Pages, and retained CSV are open/plain. | Public analytics showcase or demo. | "Fully open analytics." |

## Recommended User-Facing Choices

The setup UI should avoid asking users to reason directly over every low-level
permutation first. It should start with intent profiles, then show the derived
settings.

Recommended profiles:

- Store only: collect and retain data, publish nothing.
- Private README dashboard: commit rich README metrics, no Pages dashboard.
- Keyed dashboard: publish encrypted Pages output, key required to unlock.
- Plain dashboard: write unencrypted Pages output.
- Fully open metrics: README and Pages enabled, retained artifact plain only
  when explicitly selected.

Each profile should show:

- who can see README metrics
- who can see Pages dashboard data
- who can access retained artifacts
- whether a dashboard secret is required
- whether the user can later switch modes without losing retained history

## Presentation Principles

- Treat README dashboard as a full static dashboard, not merely a summary.
- Make "commit data" vs "artifact data" visible to users. Committed data is
  harder to fully erase than a retained artifact.
- Explain that encrypted Pages protects dashboard payload data, not the
  integrity of a compromised hosting surface.
- Explain that repository visibility is not the same as output encryption.
- Warn when a configuration mixes encrypted UI with plain retained artifacts,
  because users often assume the key protects all data.

