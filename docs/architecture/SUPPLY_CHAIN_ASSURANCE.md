# Supply Chain Assurance

Status: proposal for pre-release public hardening.

This repository publishes a generated template shell. Runtime behavior is delivered by `reponomics-dashboard-action`, so assurance priorities are split across two artifacts:

1. generated template repository contents
2. runtime action reference used by generated workflows

## Assurance Priorities

### P0: Runtime Action Authenticity

The strongest user-impacting trust boundary is the action reference in template workflows:

```yaml
uses: reponomics/reponomics-dashboard-action@v0.19.0
```

Recommended policy:

- pin to accepted release refs only
- record the accepted release tag and target commit in `template-action-release.yml`
- copy that resolved commit into generated collect/publish provenance so automatic publish can run the action revision paired with the collect run
- prefer commit-SHA pinning for highest supply-chain assurance when release ergonomics permit
- publish release notes and compatibility policy in the action repository

### P1: Template Build Provenance

For each template publication run, users should be able to prove:

- source repository: `reponomics-dashboard-dev`
- source commit and release tag
- builder workflow identity (`DEV / Publish Template Repository`)
- exact generated `dist/template` file set

Recommended mechanism:

- generate an immutable `dist/template` archive in CI
- produce a provenance attestation for that archive
- retain attestation and archive as release/build artifacts

### P1: Publication Traceability

Publishing to `reponomics-dashboard` should remain deterministic:

- commit message includes source commit metadata
- publication is tied to a release event in dashboard-dev
- only generated outputs are published

## SBOM Scope

This template is intentionally thin, so SBOM value is mostly inventory-level:

- workflow stubs
- docs/config shell files
- external GitHub Actions and runtime action references

There are no substantial packaged runtime dependencies in the generated template itself. Most dependency risk and SBOM value lives in `reponomics-dashboard-action`.

Recommended SBOM treatment:

- emit a lightweight SPDX/CycloneDX document for generated template contents
- include referenced workflow actions and pinned refs
- treat the runtime action repository SBOM as the primary dependency SBOM

## Practical Rollout

1. Add provenance generation to `DEV / Publish Template Repository`.
2. Archive generated template tarball + checksum + attestation per release.
3. Add a lightweight template SBOM artifact.
4. Document user verification steps in public docs.

## Non-Goals

- This does not replace runtime action release hardening.
- This does not claim that template attestations alone secure runtime behavior.
