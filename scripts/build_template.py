"""Build and verify the generated template repository tree."""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "template-manifest.yml"
DEFAULT_OUTPUT = ROOT / "dist" / "template"


class TemplateBuildError(RuntimeError):
    """Raised when the template output cannot be generated or verified."""


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}
    if manifest.get("version") != 1:
        raise TemplateBuildError(f"{path} must declare version: 1")
    if not manifest.get("include"):
        raise TemplateBuildError(f"{path} must include at least one path")
    return manifest


def _relative(path: Path) -> str:
    return path.as_posix().lstrip("/")


def _matches_path(path: str, pattern: str) -> bool:
    normalized = pattern.rstrip("/")
    return (
        path == normalized
        or path.startswith(f"{normalized}/")
        or fnmatch.fnmatch(path, pattern)
    )


def _copy_path(source: Path, destination: Path) -> None:
    if not source.exists():
        raise TemplateBuildError(f"Manifest includes missing path: {source}")
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _git_value(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def build_template(
    output_dir: Path = DEFAULT_OUTPUT,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    clean: bool = True,
) -> Path:
    manifest = load_manifest(manifest_path)
    output_dir = output_dir.resolve()

    if output_dir == ROOT or ROOT in output_dir.parents and output_dir.name == ".git":
        raise TemplateBuildError(f"Refusing unsafe output directory: {output_dir}")

    if clean and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for entry in manifest["include"]:
        relative = Path(entry)
        _copy_path(ROOT / relative, output_dir / relative)

    verify_template(output_dir, manifest_path)
    return output_dir


def iter_files(root: Path) -> list[str]:
    return sorted(
        _relative(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file()
    )


def verify_template(
    output_dir: Path = DEFAULT_OUTPUT,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> None:
    manifest = load_manifest(manifest_path)
    output_dir = output_dir.resolve()
    if not output_dir.exists():
        raise TemplateBuildError(f"Template output does not exist: {output_dir}")

    files = iter_files(output_dir)
    for entry in manifest["include"]:
        source = ROOT / entry
        target = output_dir / entry
        if source.is_file() and not target.is_file():
            raise TemplateBuildError(f"Required file missing from output: {entry}")
        if source.is_dir() and not target.exists():
            raise TemplateBuildError(f"Required directory missing from output: {entry}")

    forbidden = manifest.get("forbidden", [])
    leaks = [
        path
        for path in files
        for pattern in forbidden
        if _matches_path(path, pattern)
    ]
    if leaks:
        formatted = "\n".join(f"  - {path}" for path in sorted(set(leaks)))
        raise TemplateBuildError(f"Forbidden paths found in template output:\n{formatted}")

    commit = _git_value("rev-parse", "--short", "HEAD")
    print(
        f"Verified template output at {output_dir} "
        f"({len(files)} files, source={commit or 'unknown'})"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory to write the generated template tree.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Template manifest path.",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify an existing output tree without rebuilding it.",
    )
    args = parser.parse_args()

    if args.verify_only:
        verify_template(args.output, args.manifest)
    else:
        output_dir = build_template(args.output, args.manifest)
        print(f"Built template output in {output_dir}")


if __name__ == "__main__":
    main()
