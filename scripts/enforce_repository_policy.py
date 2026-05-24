"""Enforce GitHub repository settings for the generated-repo model."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, field
from typing import Any


OWNER = "reponomics"


@dataclass(frozen=True)
class RepoPolicy:
    repo: str
    is_template: bool = False
    has_issues: bool = False
    has_projects: bool = False
    has_wiki: bool = False
    has_discussions: bool = False
    has_downloads: bool = False
    has_pull_requests: bool = False
    allow_merge_commit: bool = False
    allow_squash_merge: bool = False
    allow_rebase_merge: bool = False
    allow_auto_merge: bool = False
    delete_branch_on_merge: bool = True
    allow_update_branch: bool = False
    workflows_enable: tuple[str, ...] = ()
    workflows_disable: tuple[str, ...] = ()
    vulnerability_alerts: bool | None = None
    dependabot_security_updates: bool | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


POLICIES = {
    "dev": RepoPolicy(
        repo="reponomics-dashboard-dev",
        has_pull_requests=True,
        allow_squash_merge=True,
        delete_branch_on_merge=True,
        workflows_enable=("Maintainer CI",),
        workflows_disable=("Set up traffic dashboard", "Rotate dashboard key"),
        vulnerability_alerts=True,
        dependabot_security_updates=None,
        notes=(
            "Source repo keeps maintainer CI active.",
            "Pull requests stay available for source review workflows.",
            "Dependency/security alerts remain enabled for repository health.",
        ),
    ),
    "action": RepoPolicy(
        repo="reponomics-dashboard-action",
        has_pull_requests=True,
        allow_squash_merge=True,
        delete_branch_on_merge=True,
        vulnerability_alerts=True,
        dependabot_security_updates=None,
        notes=(
            "Runtime action repo is the versioned behavior and dashboard update channel.",
            "Pull requests stay available for action changes and release review.",
            "Dependency/security alerts remain enabled for runtime health.",
        ),
    ),
    "template": RepoPolicy(
        repo="reponomics-dashboard",
        is_template=True,
        has_pull_requests=True,
        allow_squash_merge=True,
        delete_branch_on_merge=True,
        workflows_disable=(
            "Maintainer CI",
            "Set up traffic dashboard",
            "Rotate dashboard key",
        ),
        vulnerability_alerts=True,
        dependabot_security_updates=None,
        notes=(
            "Generated template repo should expose the template surface only.",
            "Pull requests stay available for pre-launch review and repository health posture.",
            "Security/dependency alerts remain enabled for launch posture.",
        ),
    ),
    "demo": RepoPolicy(
        repo="reponomics-dashboard-demo",
        allow_squash_merge=True,
        workflows_disable=(
            "Collect GitHub Traffic",
            "Set up traffic dashboard",
            "Rotate dashboard key",
        ),
        vulnerability_alerts=False,
        dependabot_security_updates=False,
        notes=(
            "Demo repo is a generated showcase artifact.",
            "No live collection, setup, rotation, pull requests, Dependabot, issues, projects, wiki, or discussions.",
        ),
    ),
}


class PolicyError(RuntimeError):
    """Raised when repository policy enforcement fails."""


def _run(args: list[str], *, dry_run: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    printable = " ".join(args)
    if dry_run:
        print(f"DRY-RUN {printable}")
        return subprocess.CompletedProcess(args, 0, "", "")
    print(printable)
    return subprocess.run(args, text=True, capture_output=True, check=check)


def _gh_json(args: list[str]) -> Any:
    completed = subprocess.run(
        ["gh", *args],
        text=True,
        capture_output=True,
        check=True,
    )
    if not completed.stdout.strip():
        return None
    return json.loads(completed.stdout)


def _repo_path(policy: RepoPolicy) -> str:
    return f"{OWNER}/{policy.repo}"


def _bool_string(value: bool) -> str:
    return "true" if value else "false"


def patch_repo(policy: RepoPolicy, *, dry_run: bool) -> None:
    fields = {
        "is_template": policy.is_template,
        "has_issues": policy.has_issues,
        "has_projects": policy.has_projects,
        "has_wiki": policy.has_wiki,
        "has_discussions": policy.has_discussions,
        "has_downloads": policy.has_downloads,
        "has_pull_requests": policy.has_pull_requests,
        "allow_merge_commit": policy.allow_merge_commit,
        "allow_squash_merge": policy.allow_squash_merge,
        "allow_rebase_merge": policy.allow_rebase_merge,
        "allow_auto_merge": policy.allow_auto_merge,
        "delete_branch_on_merge": policy.delete_branch_on_merge,
        "allow_update_branch": policy.allow_update_branch,
    }
    args = ["gh", "api", "-X", "PATCH", f"repos/{_repo_path(policy)}"]
    for key, value in fields.items():
        args.extend(["-F", f"{key}={_bool_string(value)}"])
    _run(args, dry_run=dry_run)


def list_workflows(policy: RepoPolicy) -> dict[str, str]:
    workflows = _gh_json([
        "workflow",
        "list",
        "--repo",
        _repo_path(policy),
        "--all",
        "--json",
        "name,state",
    ])
    return {workflow["name"]: workflow["state"] for workflow in workflows}


def enforce_workflows(policy: RepoPolicy, *, dry_run: bool) -> None:
    workflows = list_workflows(policy)
    for name in policy.workflows_enable:
        if name in workflows and workflows[name] != "active":
            _run(["gh", "workflow", "enable", name, "--repo", _repo_path(policy)], dry_run=dry_run)
    for name in policy.workflows_disable:
        if name in workflows and workflows[name] != "disabled_manually":
            _run(["gh", "workflow", "disable", name, "--repo", _repo_path(policy)], dry_run=dry_run)


def _toggle_endpoint(path: str, enabled: bool, *, dry_run: bool) -> None:
    method = "PUT" if enabled else "DELETE"
    completed = _run(["gh", "api", "-X", method, path], dry_run=dry_run, check=False)
    if dry_run:
        return
    if completed.returncode not in {0, 1}:
        raise PolicyError(completed.stderr.strip() or f"Failed to update {path}")
    benign_disabled_security = (
        not enabled
        and "Vulnerability alerts must be enabled" in completed.stderr
    )
    if completed.returncode == 1 and "Not Found" not in completed.stderr and not benign_disabled_security:
        raise PolicyError(completed.stderr.strip() or f"Failed to update {path}")


def enforce_security(policy: RepoPolicy, *, dry_run: bool) -> None:
    repo_path = _repo_path(policy)
    if policy.vulnerability_alerts is not None:
        _toggle_endpoint(
            f"repos/{repo_path}/vulnerability-alerts",
            policy.vulnerability_alerts,
            dry_run=dry_run,
        )
    if policy.dependabot_security_updates is not None:
        _toggle_endpoint(
            f"repos/{repo_path}/automated-security-fixes",
            policy.dependabot_security_updates,
            dry_run=dry_run,
        )


def print_summary(policy: RepoPolicy) -> None:
    repo = _gh_json([
        "api",
        f"repos/{_repo_path(policy)}",
        "--jq",
        (
            "{name,is_template,has_issues,has_projects,has_wiki,has_discussions,"
            "has_downloads,has_pull_requests,allow_forking,allow_merge_commit,"
            "allow_squash_merge,allow_rebase_merge,allow_auto_merge,"
            "delete_branch_on_merge,allow_update_branch}"
        ),
    ])
    workflows = list_workflows(policy)
    print(json.dumps({"repo": repo, "workflows": workflows, "notes": policy.notes}, indent=2))


def enforce(policy: RepoPolicy, *, dry_run: bool) -> None:
    print(f"\n== {_repo_path(policy)} ==")
    patch_repo(policy, dry_run=dry_run)
    enforce_workflows(policy, dry_run=dry_run)
    enforce_security(policy, dry_run=dry_run)
    if not dry_run:
        print_summary(policy)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        choices=tuple(POLICIES) + ("all",),
        default="all",
        help="Repository policy to enforce.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    selected = POLICIES.values() if args.repo == "all" else [POLICIES[args.repo]]
    for policy in selected:
        enforce(policy, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
