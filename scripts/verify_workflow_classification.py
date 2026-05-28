"""Verify workflow classification boundaries for dashboard-dev vs template."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
MANIFEST_PATH = ROOT / "template-manifest.yml"

TEMPLATE_WORKFLOWS = {
    "collect.yml.disabled",
    "incident-sentinel.yml.disabled",
    "keepalive.yml.disabled",
    "publish.yml.disabled",
    "rotate-key.yml",
    "setup.yml",
}
DEV_WORKFLOW_PREFIX = "dev-"
DEV_WORKFLOW_GLOB = ".github/workflows/dev-*.yml"


class WorkflowClassificationError(RuntimeError):
    """Raised when workflow boundaries are violated."""


def _load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}
    if manifest.get("version") != 1:
        raise WorkflowClassificationError(f"{path} must declare version: 1")
    return manifest


def _iter_workflow_files() -> list[str]:
    if not WORKFLOW_DIR.exists():
        raise WorkflowClassificationError(f"Missing workflow directory: {WORKFLOW_DIR}")
    return sorted(path.name for path in WORKFLOW_DIR.iterdir() if path.is_file())


def _verify_workflow_filenames(workflow_files: list[str]) -> None:
    violations: list[str] = []
    for name in workflow_files:
        if name in TEMPLATE_WORKFLOWS:
            continue
        if name.startswith(DEV_WORKFLOW_PREFIX) and name.endswith(".yml"):
            continue
        violations.append(name)
    if violations:
        listed = "\n".join(f"  - {name}" for name in violations)
        raise WorkflowClassificationError(
            "Unclassified workflow files detected. Use template canonical names "
            f"or `{DEV_WORKFLOW_PREFIX}*.yml` for maintainer workflows:\n{listed}"
        )


def _verify_manifest_includes(manifest: dict[str, Any]) -> None:
    include = manifest.get("include", [])
    workflow_entries = sorted(
        entry
        for entry in include
        if isinstance(entry, str) and entry.startswith(".github/workflows/")
    )
    expected_entries = sorted(
        f".github/workflows/{name}" for name in TEMPLATE_WORKFLOWS
    )
    if workflow_entries != expected_entries:
        expected = "\n".join(f"  - {entry}" for entry in expected_entries)
        actual = "\n".join(f"  - {entry}" for entry in workflow_entries)
        raise WorkflowClassificationError(
            "Template manifest workflow include set must match template workflow "
            f"surface exactly.\nExpected:\n{expected}\nActual:\n{actual}"
        )


def _verify_manifest_forbidden(manifest: dict[str, Any]) -> None:
    forbidden = manifest.get("forbidden", [])
    if DEV_WORKFLOW_GLOB not in forbidden:
        raise WorkflowClassificationError(
            f"template-manifest forbidden list must include `{DEV_WORKFLOW_GLOB}`"
        )


def verify() -> None:
    workflow_files = _iter_workflow_files()
    manifest = _load_manifest()
    _verify_workflow_filenames(workflow_files)
    _verify_manifest_includes(manifest)
    _verify_manifest_forbidden(manifest)
    print(
        f"Verified workflow classification "
        f"({len(workflow_files)} workflow files, {len(TEMPLATE_WORKFLOWS)} template files)"
    )


if __name__ == "__main__":
    try:
        verify()
    except WorkflowClassificationError as exc:
        print(f"Workflow classification error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
