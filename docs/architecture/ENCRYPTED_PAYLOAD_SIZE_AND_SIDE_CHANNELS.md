# Encrypted Payload Size And Side Channels

This note records current findings about encrypted GitHub Pages dashboard
payload size, metadata leakage, and low-cost mitigations.

## Context

Encrypted Pages mode currently publishes a plaintext dashboard shell containing
an encrypted JSON payload in a script tag:

```html
<script id="encrypted-payload" type="application/json">...</script>
```

The encrypted payload protects dashboard contents from viewers without
`TRAFFIC_DASHBOARD_SECRET`, but it does not make the public file opaque in every
respect. Observers can still see:

- the existence of the dashboard
- publication timing
- encrypted payload length
- payload length changes across commits
- static shell changes

The payload length side channel is not a hard blocker for the product's current
threat model, but it should be handled deliberately.

## Current Findings

The renderer lives in `reponomics-action`, not this template repository. As of
the current implementation, the encrypted dashboard plaintext is compact JSON
from the shared dashboard payload. It is encrypted with AES-GCM and then
base64-encoded into the published HTML.

The payload is not only a simple repo-by-day table. It includes aggregate daily
series, per-repo daily series, repository growth data, latest top referrer
snapshots, latest top path snapshots, and structured insight data. This makes
payload size sensitive to:

- number of tracked repositories
- retained day count
- repo name length
- path and title length
- top path and top referrer row count
- repeated data shapes kept for frontend convenience

A real template-derived test repository with only two tracked repos and one or
two collection runs produced an encrypted payload of roughly 150 KB. That is
plausible because first collection can already include GitHub's recent rolling
traffic window, and path/title strings can dominate payload size.

Synthetic estimates using the current action payload builder produced these
rough magnitudes:

| Scenario | Plain payload | Encrypted payload JSON |
| --- | ---: | ---: |
| 50 repos, 1 day, no top paths/referrers | ~63 KB | ~84 KB |
| 50 repos, 1 day, top 1 path/referrer per repo | ~86 KB | ~115 KB |
| 50 repos, 1 day, top 10 paths/referrers per repo | ~254 KB | ~338 KB |
| 50 repos, 14 days, top 10 paths/referrers per repo | ~303 KB | ~405 KB |
| 50 repos, 90 days, top 10 paths/referrers per repo | ~560 KB | ~747 KB |

These estimates are not contractual limits. They demonstrate scale: a 64 KB
padding bucket is already too small for realistic encrypted Pages output.

## What Length Reveals

Payload length does not reveal repo names, traffic counts, referrers, paths, or
growth trends directly. With a strong dashboard secret, AES-GCM prevents content
inspection.

However, length can reveal approximate scale:

- tiny versus large dashboard
- rough number of tracked repositories
- whether top path/referrer data is sparse or dense
- whether retained history has grown
- whether a publish introduced a large payload change

This is a metadata leak, not plaintext disclosure. The documentation should say
that encrypted Pages hides dashboard contents, not dashboard size, update
timing, or the existence of the dashboard.

## One-Line Payload Risk

There is no product-safe assumption that a single line of text can grow without
practical limits. Browsers and Git can often handle a one-line megabyte-scale
script payload, but long lines are hostile to the surrounding toolchain:

- Git diffs become unreadable.
- GitHub web diffs may be truncated or suppressed.
- Editors and review tools may slow down or fail line-oriented operations.
- Formatters, linters, scanners, and shell tools may have line-length or memory
  behavior that differs from browser behavior.
- Copy/paste and manual inspection become unreliable.

The public encrypted payload should therefore be treated as a large binary-like
artifact, even though it is text. Prefer chunking, pretty metadata, or a
separate payload file when implementation cost is acceptable.

## Trust And Verifiability Stance

The primary user experience should not require users to reason deeply about
supply-chain provenance. However, the product should be prepared for scrutiny
from security-focused users and researchers who want to verify the trust
boundary before running Reponomics or publishing a dashboard.

The defensible claim is not that Reponomics can prove its code is benevolent.
The defensible claim is that Reponomics can make the trust boundary inspectable:

```text
Security-focused users can inspect the exact action source for a specific
release, pin their workflow to that exact commit, verify the release provenance,
and inspect decrypted payload data through a data-only path that does not
execute generated dashboard code.
```

This is a provenance and auditability guarantee, not a non-malice guarantee.
Open source, immutable releases, release attestations, and full-SHA workflow
pinning can give users strong confidence that the code they run is the code they
had the opportunity to inspect. They do not remove the need to evaluate what
that code does.

The recommended high-scrutiny posture is:

- keep the action source small enough to audit
- keep runtime dependencies minimal, pinned, and visible in release materials
- vendor and pin browser rendering assets, such as Chart.js
- publish immutable releases with provenance attestations
- document the release commit SHA and security-relevant changes
- allow users to pin workflows to a full commit SHA instead of a moving tag
- provide a local data-only decrypt/inspect tool that never parses dashboard
  HTML, executes dashboard JavaScript, imports remote code, or fetches network
  resources
- make generated payload files separable from executable dashboard shell files

The strongest user-facing wording is:

```text
Reponomics cannot eliminate trust. It can narrow trust to auditable code and
verifiable release provenance. Users who need that assurance can review a
specific release, pin to its full commit SHA, verify release provenance, and
inspect encrypted payload contents with a non-executing decrypt tool before
publishing or opening the dashboard.
```

## Mitigation Options

### Bucket Padding

Pad the dashboard plaintext before encryption. Store the true unpadded length
inside the encrypted plaintext, not in public metadata.

Recommended default:

```text
512 KiB plaintext floor
512 KiB plaintext buckets
```

This is cheap and easy to explain. It hides precise payload size for small and
medium dashboards without forcing every Pages load into multi-megabyte output.
A stronger but more wasteful variant is a 1 MiB floor with 1 MiB buckets.

Pros:

- directly reduces size side-channel precision
- simple to test
- independent of data model optimizations
- compatible with current AES-GCM flow

Cons:

- increases Pages payload size
- still leaks bucket crossings
- does not improve diff readability by itself

### Payload Normalization

Reduce repeated strings and duplicated structures before encryption.

Recommended changes:

- encode repositories once and refer to them by integer id
- encode owners once instead of repeating full `owner/repo` strings
- encode common path prefixes, such as repo roots and `/blob/<branch>/`
- represent hot tables like paths and referrers as compact row arrays
- avoid shipping both global and per-repo structures when one can be derived
  client-side

Pros:

- reduces bandwidth
- reduces Pages load time
- makes padding cheaper
- improves future schema migration discipline

Cons:

- adds a payload schema migration
- adds frontend decode logic
- does not by itself eliminate size leakage

### Compression

Compress the JSON before encryption, then pad the compressed bytes.

Pros:

- likely large reduction because the payload contains repeated keys and strings
- keeps the logical payload schema mostly unchanged
- makes padding cheaper

Cons:

- requires browser-side decompression support or an embedded decompressor
- adds compatibility and testing surface
- compression is size optimization, not a full metadata defense

If compression is added, the order should be:

```text
JSON payload
compress
pad
encrypt
base64 or chunk for transport
```

Padding before compression is ineffective because compression removes much of
the padding.

### Payload Chunking Or External Payload File

Keep the dashboard shell readable and move the encrypted payload into chunks or
a separate file such as `docs/assets/dashboard-payload.enc.json`.

Pros:

- improves diffs for `docs/index.html`
- avoids one-line megabyte-scale HTML
- makes encrypted output easier to treat as generated data

Cons:

- does not reduce size leakage on its own
- adds another Pages asset and fetch path if externalized
- standalone/offline dashboard needs an inline or bundled variant

### Git Diff Attributes

Use `.gitattributes` to make encrypted payload files behave like opaque
generated blobs in Git diffs.

Preferred split:

```gitattributes
docs/index.html diff=html
docs/assets/dashboard-payload.enc.json -diff
```

This keeps the dashboard shell reviewable while suppressing unreadable
ciphertext diffs. If encrypted payloads remain embedded directly in
`docs/index.html`, the project can still mark that file as `-diff`, but that is
a worse tradeoff because it hides meaningful shell changes along with the
payload.

For local-only experiments, the same attributes can be placed in
`.git/info/attributes`. Product defaults should use a committed
`.gitattributes` entry so generated repositories behave consistently on GitHub
and in local clones.

Pros:

- cheap to implement
- improves review ergonomics immediately
- works even before payload normalization or padding
- pairs naturally with external encrypted payload files

Cons:

- does not reduce payload size
- does not reduce size side-channel leakage
- can hide meaningful changes if applied to a mixed shell-plus-payload file

## Recommendation

Use a layered mitigation:

1. Add payload normalization for repeated repo and path data.
2. Add plaintext bucket padding before AES-GCM encryption.
3. Use a 512 KiB floor and 512 KiB buckets as the first default.
4. Chunk or externalize the encrypted payload so `docs/index.html` remains
   reviewable.
5. Mark the external encrypted payload path as `-diff` in committed
   `.gitattributes`.
6. Consider compression later if measured payload size remains awkward.

This keeps the product honest: encrypted Pages protects data contents, while
normalization and padding reduce bandwidth cost and size-based metadata leakage.
