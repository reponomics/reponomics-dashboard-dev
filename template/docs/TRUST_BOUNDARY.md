# Repository Trust Boundary

> [!WARNING]
> Pre-release placeholder guidance.

Access to this repository is part of the dashboard security model.

## What Repository Access Can Control

People with write/admin access can change workflows, configuration, and retained artifact behavior. Treat repository write access as control-plane trust, not only report visibility.

## Private Repositories

Private visibility limits repository access, but collaborators with elevated permissions can still alter workflow behavior. Grant permissions intentionally.

## Public Repositories

Use encrypted privacy modes for dashboards and assume workflow metadata and repository changes are visible.
