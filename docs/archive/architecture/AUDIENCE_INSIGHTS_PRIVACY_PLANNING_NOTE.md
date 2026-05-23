# Audience Insights Privacy Planning Note

Status: provisional planning note, not accepted scope

Date: 2026-05-16

## Context

Reponomics is primarily a private repository growth dashboard. The default
product collects and renders aggregate repository metrics such as views,
visitors, clones, stars, subscribers, and forks. Those metrics describe
repositories and are appropriate for the existing README, Pages, and artifact
privacy modes.

A future feature class is possible: audience insights derived from public GitHub
identity events, such as stargazer or forker lists. These could support useful
portfolio analytics:

- which repositories share the same audience
- whether one repository attracts a distinct audience
- whether users tend to star or fork one repository before another
- whether adoption signals cluster around a subset of related repositories
- whether a repository has high attention but low audience conversion

This is analytically valuable, but it is qualitatively different from aggregate
repo counters. A single public star is public. A retained cross-repository graph
of who starred or forked what, and when, is a derived behavioral dataset.

## Provisional Product Boundary

Audience identity or cohort analytics should not be part of the default
Reponomics path.

If implemented later, they should be an explicit private-audience mode with
enforced privacy constraints, not a public leaderboard or glamour metric.

Aggregate growth metrics and audience-derived metrics should be treated as
separate data classes:

| Data class | Examples | Default publication posture |
|------------|----------|-----------------------------|
| Aggregate repository growth metrics | views, visitors, clones, stars, subscribers, forks | May be rendered in README, encrypted Pages, plain Pages, and encrypted/plain artifacts according to the user's selected disclosure mode. |
| Audience identity/cohort metrics | stargazer overlap, forker overlap, lead/lag between repos, cohort uniqueness | Must require encrypted retained storage and encrypted or local-only rendering. Must not be rendered to public plaintext outputs. |

## Provisional Enforcement Policy

If a future `audience_insights` mode is enabled, setup and runtime validation
should reject incompatible disclosure settings.

Allowed:

- `artifact-security-mode: encrypted`
- `pages-dashboard: encrypted`
- `pages-dashboard: disabled` for store-only or local/offline workflows
- local/offline inspection paths, if implemented

Forbidden:

- `artifact-security-mode: plain`
- `pages-dashboard: plain`
- `readme-dashboard: enabled`
- plaintext standalone dashboard artifacts containing audience-derived metrics

The product should enforce this. It should not only warn.

## Possible Future Configuration Shape

This is illustrative, not a committed schema:

```yaml
audience_insights:
  enabled: false
  collect_stargazers: false
  collect_forkers: false
  hash_identities: true
  retain_raw_logins: false
  retention_days: 90
```

If identities are retained, the safer default should be salted or keyed hashes
rather than raw logins:

```text
repo,subject_type,subject_hash,observed_at,event_ts,source,schema_version
```

Aggregate materializations could then support dashboard rendering without
exposing raw identities:

```text
repo_a,repo_b,subject_type,overlap_count,a_share,b_share,jaccard,computed_at
```

## Rendering Principles

Default rendered audience insights should describe cohorts, not individuals:

- "Repo A and Repo B share 64% of observed stargazers."
- "Repo C has the most distinct audience in the tracked portfolio."
- "Forker overlap is concentrated around these two repositories."

The README should never render audience identity or cohort-derived metrics.
Plain Pages should never render audience identity or cohort-derived metrics.
Encrypted Pages may render aggregate cohort insights if the mode is explicitly
enabled and retained artifacts are encrypted.

## Open Questions

- Should raw logins ever be retained, even in encrypted/private mode?
- Should a separate secret be required for audience identity hashing?
- Should audience insights require a different setup confirmation than normal
  encrypted dashboard mode?
- What retention period is appropriate for identity-derived observations?
- Should local/offline inspection expose more detail than encrypted Pages?
- How should the product describe public-source, private-derived data without
  minimizing the privacy implications?

## Non-Goals

This note does not propose implementing audience insights for v1.

It does not change the default aggregate growth metrics plan. Stars,
subscribers, forks, views, visitors, and clones remain aggregate repository
metrics and can use the existing disclosure model.

