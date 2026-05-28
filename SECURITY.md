# Security Policy

This repository is in a public pre-release hardening period. This is the development repository that produces the Reponomics Dashboard template repo as a generated output. It is tightly coupled with the [Reponomics Dashboard Action](https://github.com/reponomics/reponomics-dashboard-action) repository, and it contains workflows that are the primary intended consumers for that action. Although it is not yet recommended for public use, security reports are welcome even before general adoption is invited.

## Supported Versions

No stable production version is supported yet. Until the first stable release, security fixes will generally land on `main` and then be included in the next pre-release or release tag.

Before `v1`, users should not expect seamless updates between versions. Security fixes may be released together with incompatible pre-release changes, and migration guidance may require manual review.

After stable release, this policy will be updated with the supported major version line and expected fix process.

## Reporting a Vulnerability

Please do not open a public issue for a suspected vulnerability.

Use GitHub [private vulnerability reporting](https://github.com/reponomics/reponomics-dashboard-dev/security/advisories/new) for this repository. You will receive a response with 48 hours and we will determine the appropriate method and timeline for a resolution if a problem is identified.

Useful reports include:

- affected commit, tag, or workflow run;
- a concise description of the vulnerability;
- reproduction steps using synthetic or redacted data;
- expected impact;
- whether any token, secret, or generated dashboard output may have been exposed.

## Scope

In scope:

- generated dashboard HTML and JavaScript;
- dashboard encryption and decryption behavior;
- retained dashboard data artifact encryption, restore, and upload behavior;
- workflow permissions, token handling, and release automation;
- vendored browser assets and their recorded upstream metadata;
- release notice parsing and rendering;
- action inputs and outputs that may expose sensitive data.

Out of scope:

- denial-of-service reports without a plausible security impact;
- reports that require access to a user's own GitHub token, repository settings, or dashboard secret without another vulnerability;
- social engineering, phishing, or physical attacks;
- vulnerability reports based only on unsupported or intentionally weakened configuration, such as opting into weak dashboard secrets ("casual" privacy mode).

## Disclosure

Maintainers will assess reports and coordinate fixes according to severity and project stage. Because this is pre-release software, the usual resolution may be a fix on `main`, updated documentation, or a temporary warning against a configuration until a fuller mitigation is available.
