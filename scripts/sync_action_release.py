"""Synchronize the template's accepted Reponomics action release."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "template-action-release.yml"
ACTION_REPOSITORY = "reponomics/reponomics-dashboard-action"
GITHUB_API = "https://api.github.com"
REQUEST_TIMEOUT_SECONDS = 20
SEMVER_TAG_RE = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ACTION_REF_RE = re.compile(
    r"reponomics/reponomics-dashboard-action@v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
)
ACTION_REF_ENV_RE = re.compile(
    r'^(?P<prefix>\s+REPONOMICS_ACTION_REF: ")'
    r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r'(?P<suffix>")$'
)
ACTION_SHA_ENV_RE = re.compile(
    r'^(?P<prefix>\s+REPONOMICS_ACTION_SHA: ")[0-9a-f]{40}(?P<suffix>")$'
)
STATUS_LINE_RE = re.compile(
    r"^(?P<prefix>Status: current(?: docs are aligned with the action| for action) `)"
    r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?P<suffix>`.*)$"
)

MANAGED_TEXT_PATHS = [
    "README.md",
    "docs/GENERATED_REPOSITORY_MODEL.md",
    "docs/README.md",
    "docs/adr/0003-generated-template-and-demo-repositories.md",
    "docs/architecture/ENCRYPTED_PAYLOAD_SIZE_AND_SIDE_CHANNELS.md",
    "docs/architecture/PRIVACY_CONFIGURATION_MATRIX.md",
    "docs/architecture/README.md",
    "docs/architecture/SUPPLY_CHAIN_ASSURANCE.md",
    "docs/architecture/VERSIONING_AND_UPDATES.md",
    "template/.github/workflows/collect.yml",
    "template/.github/workflows/publish.yml",
    "template/.github/workflows/rotate-key.yml",
    "tests/test_generated_repos.py",
]
SKIPPED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__INTERNAL__",
    "dist",
    "archived",
    "venv",
}
REQUIRED_ACTION_INPUTS = {"allow-docs-sync"}
REQUIRED_ACTION_OUTPUTS = {"docs-sync-state", "docs-action-version", "docs-updated-at"}


class ActionReleaseError(RuntimeError):
    """Raised when the accepted action release metadata is invalid or stale."""


@dataclass(frozen=True)
class ActionRelease:
    repository: str
    tag: str
    target_commitish: str
    release_url: str
    published_at: str

    @property
    def version(self) -> str:
        return self.tag.removeprefix("v")


def _request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "reponomics-dashboard-dev-action-release-sync",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ActionReleaseError(f"Could not fetch {url}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ActionReleaseError(f"Expected object response from {url}")
    return payload


def _request_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "reponomics-dashboard-dev-action-release-sync"},
    )
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise ActionReleaseError(f"Could not fetch {url}: {exc}") from exc


def _validate_tag(tag: str) -> None:
    if not SEMVER_TAG_RE.match(tag):
        raise ActionReleaseError(f"Action release tag must be exact SemVer, got {tag!r}")


def _validate_sha(value: str) -> None:
    if not SHA_RE.match(value):
        raise ActionReleaseError(f"Action release target must be a 40-character SHA, got {value!r}")


def _tag_commit_sha(repository: str, tag: str) -> str:
    ref = _request_json(f"{GITHUB_API}/repos/{repository}/git/ref/tags/{tag}")
    obj = ref.get("object")
    if not isinstance(obj, dict):
        raise ActionReleaseError(f"Tag ref for {repository}@{tag} has no object")
    obj_type = str(obj.get("type") or "")
    obj_sha = str(obj.get("sha") or "")
    if obj_type == "commit":
        _validate_sha(obj_sha)
        return obj_sha
    if obj_type == "tag":
        tag_obj = _request_json(f"{GITHUB_API}/repos/{repository}/git/tags/{obj_sha}")
        target = tag_obj.get("object")
        if isinstance(target, dict) and target.get("type") == "commit":
            target_sha = str(target.get("sha") or "")
            _validate_sha(target_sha)
            return target_sha
    raise ActionReleaseError(f"Could not resolve {repository}@{tag} to a commit SHA")


def fetch_release(repository: str, tag: str) -> ActionRelease:
    _validate_tag(tag)
    payload = _request_json(f"{GITHUB_API}/repos/{repository}/releases/tags/{tag}")
    if payload.get("draft") or payload.get("prerelease"):
        raise ActionReleaseError(f"{repository}@{tag} must be a published stable release")
    target = str(payload.get("target_commitish") or "")
    if not SHA_RE.match(target):
        target = _tag_commit_sha(repository, tag)
    release = ActionRelease(
        repository=repository,
        tag=str(payload.get("tag_name") or ""),
        target_commitish=target,
        release_url=str(payload.get("html_url") or ""),
        published_at=str(payload.get("published_at") or ""),
    )
    validate_release(release)
    return release


def fetch_action_yml(release: ActionRelease) -> str:
    return _request_text(
        f"https://raw.githubusercontent.com/{release.repository}/{release.tag}/action.yml"
    )


def validate_release(release: ActionRelease) -> None:
    if release.repository != ACTION_REPOSITORY:
        raise ActionReleaseError(
            f"Action repository must be {ACTION_REPOSITORY}, got {release.repository!r}"
        )
    _validate_tag(release.tag)
    _validate_sha(release.target_commitish)
    expected_url = f"https://github.com/{release.repository}/releases/tag/{release.tag}"
    if release.release_url != expected_url:
        raise ActionReleaseError(f"Release URL must be {expected_url}, got {release.release_url!r}")
    if not release.published_at:
        raise ActionReleaseError("Release published_at must be set")


def validate_action_metadata(action_yml: str) -> None:
    payload = yaml.safe_load(action_yml) or {}
    if not isinstance(payload, dict):
        raise ActionReleaseError("action.yml must parse as a YAML object")
    inputs = payload.get("inputs")
    outputs = payload.get("outputs")
    if not isinstance(inputs, dict) or not isinstance(outputs, dict):
        raise ActionReleaseError("action.yml must declare inputs and outputs")
    mode = inputs.get("mode")
    if not isinstance(mode, dict) or "docs-sync" not in str(mode.get("description") or ""):
        raise ActionReleaseError("action.yml mode input must document docs-sync")
    missing_inputs = REQUIRED_ACTION_INPUTS - set(inputs)
    if missing_inputs:
        raise ActionReleaseError(
            "action.yml is missing required docs-sync input(s): "
            + ", ".join(sorted(missing_inputs))
        )
    missing_outputs = REQUIRED_ACTION_OUTPUTS - set(outputs)
    if missing_outputs:
        raise ActionReleaseError(
            "action.yml is missing required docs-sync output(s): "
            + ", ".join(sorted(missing_outputs))
        )


def load_manifest(root: Path = ROOT) -> ActionRelease:
    path = root / "template-action-release.yml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ActionReleaseError(f"{path} must parse as a YAML object")
    if payload.get("schema_version") != 1:
        raise ActionReleaseError(f"{path} must declare schema_version: 1")
    release = ActionRelease(
        repository=str(payload.get("repository") or ""),
        tag=str(payload.get("tag") or ""),
        target_commitish=str(payload.get("target_commitish") or ""),
        release_url=str(payload.get("release_url") or ""),
        published_at=str(payload.get("published_at") or ""),
    )
    validate_release(release)
    return release


def write_manifest(release: ActionRelease, root: Path = ROOT) -> None:
    validate_release(release)
    text = "\n".join(
        [
            "schema_version: 1",
            f"repository: {release.repository}",
            f"tag: {release.tag}",
            f"target_commitish: {release.target_commitish}",
            f"release_url: {release.release_url}",
            f'published_at: "{release.published_at}"',
            "",
        ]
    )
    (root / "template-action-release.yml").write_text(text, encoding="utf-8")


def _replace_status_versions(text: str, tag: str) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        match = STATUS_LINE_RE.match(body)
        if match:
            body = f"{match.group('prefix')}{tag}{match.group('suffix')}"
        lines.append(body + newline)
    return "".join(lines)


def _replace_action_release_env(text: str, release: ActionRelease) -> str:
    lines = []
    for line in text.splitlines(keepends=True):
        newline = "\n" if line.endswith("\n") else ""
        body = line[:-1] if newline else line
        ref_match = ACTION_REF_ENV_RE.match(body)
        sha_match = ACTION_SHA_ENV_RE.match(body)
        if ref_match:
            body = f"{ref_match.group('prefix')}{release.tag}{ref_match.group('suffix')}"
        elif sha_match:
            body = (
                f"{sha_match.group('prefix')}"
                + f"{release.target_commitish}{sha_match.group('suffix')}"
            )
        lines.append(body + newline)
    return "".join(lines)


def sync_release(root: Path, release: ActionRelease, action_yml: str) -> None:
    validate_release(release)
    validate_action_metadata(action_yml)
    write_manifest(release, root)
    replacement = f"{release.repository}@{release.tag}"
    for relative in MANAGED_TEXT_PATHS:
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = ACTION_REF_RE.sub(replacement, text)
        text = _replace_status_versions(text, release.tag)
        text = _replace_action_release_env(text, release)
        path.write_text(text, encoding="utf-8")


def _iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIPPED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def _read_text_if_possible(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def verify_release(root: Path, release: ActionRelease, action_yml: str) -> None:
    validate_release(release)
    validate_action_metadata(action_yml)
    expected_ref = f"{release.repository}@{release.tag}"
    stale: list[str] = []
    for path in _iter_text_files(root):
        text = _read_text_if_possible(path)
        if not text:
            continue
        for action_ref_match in ACTION_REF_RE.finditer(text):
            if action_ref_match.group(0) != expected_ref:
                stale.append(f"{path.relative_to(root)}: {action_ref_match.group(0)}")
        for line_number, line in enumerate(text.splitlines(), start=1):
            match = STATUS_LINE_RE.match(line)
            if match and release.tag not in line:
                stale.append(f"{path.relative_to(root)}:{line_number}: {line}")
            ref_match = ACTION_REF_ENV_RE.match(line)
            if ref_match and release.tag not in line:
                stale.append(f"{path.relative_to(root)}:{line_number}: {line}")
            sha_match = ACTION_SHA_ENV_RE.match(line)
            if sha_match and release.target_commitish not in line:
                stale.append(f"{path.relative_to(root)}:{line_number}: {line}")
    if stale:
        formatted = "\n".join(f"  - {entry}" for entry in stale)
        raise ActionReleaseError(f"Stale action release references found:\n{formatted}")


def _payload_release(path: Path) -> ActionRelease:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ActionReleaseError(f"{path} must contain a JSON object")
    release = ActionRelease(
        repository=ACTION_REPOSITORY,
        tag=str(payload.get("tag_name") or payload.get("tag") or ""),
        target_commitish=str(payload.get("target_commitish") or ""),
        release_url=str(payload.get("html_url") or payload.get("release_url") or ""),
        published_at=str(payload.get("published_at") or ""),
    )
    validate_release(release)
    return release


def _load_action_yml(path: Path | None, release: ActionRelease) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")
    return fetch_action_yml(release)


def _sync(args: argparse.Namespace) -> None:
    tag = args.tag or args.action_tag
    if not tag:
        raise ActionReleaseError("sync requires --tag or ACTION_TAG")
    release = _payload_release(args.release_json) if args.release_json else fetch_release(args.repository, tag)
    if release.tag != tag:
        raise ActionReleaseError(f"Release payload tag {release.tag!r} did not match {tag!r}")
    if args.expected_target_commitish and release.target_commitish != args.expected_target_commitish:
        raise ActionReleaseError(
            "Release target did not match dispatch payload: "
            + f"{release.target_commitish} != {args.expected_target_commitish}"
        )
    if args.expected_release_url and release.release_url != args.expected_release_url:
        raise ActionReleaseError(
            f"Release URL did not match dispatch payload: {release.release_url} != {args.expected_release_url}"
        )
    action_yml = _load_action_yml(args.action_yml, release)
    sync_release(args.root, release, action_yml)
    print(f"Synchronized {release.repository}@{release.tag}")


def _verify(args: argparse.Namespace) -> None:
    release = load_manifest(args.root)
    action_yml = _load_action_yml(args.action_yml, release)
    verify_release(args.root, release, action_yml)
    print(f"Verified {release.repository}@{release.tag}")


def _print_tag(args: argparse.Namespace) -> None:
    print(load_manifest(args.root).tag)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync = subparsers.add_parser("sync", help="Update managed refs to an action release")
    sync.add_argument("--tag")
    sync.add_argument("--repository", default=ACTION_REPOSITORY)
    sync.add_argument("--release-json", type=Path)
    sync.add_argument("--action-yml", type=Path)
    sync.add_argument("--expected-target-commitish", default="")
    sync.add_argument("--expected-release-url", default="")
    sync.set_defaults(func=_sync, action_tag="")

    verify = subparsers.add_parser("verify", help="Verify managed refs match the manifest")
    verify.add_argument("--action-yml", type=Path)
    verify.set_defaults(func=_verify)

    print_tag = subparsers.add_parser("print-tag", help="Print the manifest action tag")
    print_tag.set_defaults(func=_print_tag)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "sync":
        args.action_tag = ""
        if not args.tag:
            import os

            args.action_tag = os.environ.get("ACTION_TAG", "")
    try:
        args.func(args)
    except ActionReleaseError as exc:
        print(f"Action release sync error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
