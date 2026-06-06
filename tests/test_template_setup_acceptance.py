"""Acceptance tests for setup in generated dashboard repositories."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import yaml

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_template


def _run(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


def _read_env_file(path: Path) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value
    return values


def _initialise_generated_repo(repo: Path, remote: Path) -> None:
    _run(["git", "init", "-b", "main"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.invalid"], repo, os.environ.copy())
    _run(["git", "add", "-A"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "initial template"], repo, os.environ.copy())
    _run(["git", "init", "--bare", str(remote)], repo, os.environ.copy())
    _run(["git", "remote", "add", "origin", str(remote)], repo, os.environ.copy())
    _run(["git", "push", "-u", "origin", "main"], repo, os.environ.copy())


def _setup_step_env(step_name: str, base_env: dict[str, str]) -> dict[str, str]:
    env = base_env.copy()
    if step_name == "Resolve setup modes":
        env.update(
            {
                "PRIVACY_MODE": "strong",
                "GENERATE_HTML_DASHBOARD": "false",
                "GENERATE_README": "false",
                "USE_GITHUB_APP": "true",
                "REPOSITORY_PRIVATE": "true",
            }
        )
    elif step_name == "Validate required secrets":
        env.update(
            {
                "USE_GITHUB_APP": base_env["USE_GITHUB_APP"],
                "COLLECTION_TOKEN": "",
                "COLLECTION_APP_ID_VAR": "12345",
                "COLLECTION_APP_ID_SECRET": "",
                "COLLECTION_APP_PRIVATE_KEY": "not-a-real-key-but-nonempty",
                "DASHBOARD_SECRET_DO_NOT_REPLACE": "0123456789abcdef0123456789abcdef01234567",
            }
        )
    return env


def test_generated_setup_workflow_runs_with_default_github_app_token_permissions(
    tmp_path: Path,
) -> None:
    """A generated repo setup run must not need workflow-file write permission."""
    repo = tmp_path / "repo"
    remote = tmp_path / "remote.git"
    build_template.build_template(repo)
    _initialise_generated_repo(repo, remote)

    workflow = yaml.safe_load((repo / ".github" / "workflows" / "setup.yml").read_text(encoding="utf-8"))
    run_steps = [step for step in workflow["jobs"]["setup"]["steps"] if "run" in step]
    env_file = tmp_path / "github-env"
    summary_file = tmp_path / "github-step-summary"
    workflow_env = {key: str(value) for key, value in workflow.get("env", {}).items()}
    base_env = {
        **os.environ,
        **workflow_env,
        "GITHUB_ENV": str(env_file),
        "GITHUB_STEP_SUMMARY": str(summary_file),
        "GITHUB_REPOSITORY": "owner/generated-dashboard",
        "GITHUB_REPOSITORY_OWNER": "owner",
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_SHA": _run(["git", "rev-parse", "HEAD"], repo, os.environ.copy()).stdout.strip(),
    }

    for step in run_steps:
        base_env.update(_read_env_file(env_file))
        env = _setup_step_env(step["name"], base_env)
        result = subprocess.run(
            ["bash", "-euo", "pipefail", "-c", step["run"]],
            cwd=repo,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert result.returncode == 0, (
            f"setup step failed: {step['name']}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    changed_paths = _run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        repo,
        os.environ.copy(),
    ).stdout.splitlines()
    assert not any(path.startswith(".github/workflows/") for path in changed_paths), changed_paths
