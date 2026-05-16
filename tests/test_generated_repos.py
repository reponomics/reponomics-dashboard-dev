"""Tests for generated Reponomics dashboard repository outputs."""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_template
import publish_generated_repo


def test_template_manifest_includes_thin_template_surface(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    required = [
        ".github/workflows/collect.yml.disabled",
        ".github/workflows/publish.yml.disabled",
        ".github/workflows/setup.yml",
        ".github/workflows/rotate-key.yml",
        "README.md",
        "config.yaml",
        "docs/README.md",
        "docs/SECURE_DASHBOARD_KEY.md",
        "docs/index.html",
    ]
    for relative_path in required:
        assert (output / relative_path).exists()


def test_template_manifest_excludes_action_owned_runtime(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    forbidden = [
        "requirements.txt",
        "requirements-dev.txt",
        "Makefile",
        "maintainer.mk",
        "template-manifest.yml",
        "scripts",
        "tests",
        "vendor",
        "docs/GENERATED_REPOSITORY_MODEL.md",
        "docs/REPOSITORY_POLICY.md",
        "docs/adr",
    ]
    for relative_path in forbidden:
        assert not (output / relative_path).exists()


def test_template_workflows_delegate_to_reponomics_action(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    workflows = output / ".github" / "workflows"
    collect = (workflows / "collect.yml.disabled").read_text(encoding="utf-8")
    publish = (workflows / "publish.yml.disabled").read_text(encoding="utf-8")
    setup = (workflows / "setup.yml").read_text(encoding="utf-8")
    rotate = (workflows / "rotate-key.yml").read_text(encoding="utf-8")

    assert "uses: reponomics/reponomics-action@main" in collect
    assert "uses: reponomics/reponomics-action@main" in publish
    assert "uses: reponomics/reponomics-action@main" not in setup
    assert "uses: reponomics/reponomics-action@main" in rotate
    assert "python scripts/" not in collect
    assert "python scripts/" not in publish
    assert "python scripts/" not in setup
    assert "python scripts/" not in rotate
    assert "mode: collect" in collect
    assert "mode: publish" in publish
    assert "workflow_run:" in publish


def test_setup_workflow_resolves_pages_dashboard_profiles():
    setup = Path(".github/workflows/setup.yml").read_text(encoding="utf-8")

    expected_profiles = {
        "encrypted-and-published": ("encrypted", "enabled", "encrypted"),
        "plaintext-and-published": ("plain", "enabled", "plain"),
        "encrypted-but-NOT-published": ("encrypted", "disabled", "encrypted"),
        "plaintext-but-NOT-published": ("plain", "disabled", "plain"),
    }
    for profile, (pages_mode, pages_publication, artifact_mode) in expected_profiles.items():
        assert re.search(
            rf'{profile}\)\n'
            rf'\s+pages_mode="{pages_mode}"\n'
            rf'\s+pages_publication="{pages_publication}"\n'
            rf'\s+artifact_mode="{artifact_mode}"',
            setup,
        )

    assert 'echo "PAGES_DASHBOARD=$pages_mode"' in setup
    assert 'echo "PAGES_PUBLICATION=$pages_publication"' in setup
    assert "Configure GitHub Pages publication" in setup


def test_template_docs_do_not_reference_old_brand_or_maintenance_docs(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.rglob("*")
        if path.is_file() and path.suffix in {"", ".md", ".yml", ".yaml", ".html"}
    )
    assert "github-traffic-report" not in text
    assert "hesreallyhim" not in text
    assert "GENERATED_REPOSITORY_MODEL.md" not in text
    assert "REPOSITORY_POLICY.md" not in text


def test_template_verify_rejects_forbidden_paths(tmp_path):
    output = tmp_path / "template"
    build_template.build_template(output)
    leaked = output / "scripts" / "collect.py"
    leaked.parent.mkdir()
    leaked.write_text("# leak\n", encoding="utf-8")

    with pytest.raises(build_template.TemplateBuildError):
        build_template.verify_template(output)


def test_publish_remote_safety_accepts_expected_repo():
    publish_generated_repo._assert_expected_repo(
        "git@github.com:reponomics/reponomics-dashboard.git",
        "reponomics/reponomics-dashboard",
    )
    publish_generated_repo._assert_expected_repo(
        "https://github.com/reponomics/reponomics-dashboard-demo.git",
        "reponomics/reponomics-dashboard-demo",
    )


def test_publish_remote_safety_rejects_wrong_repo():
    with pytest.raises(publish_generated_repo.PublishError):
        publish_generated_repo._assert_expected_repo(
            "git@github.com:reponomics/reponomics-dashboard-dev.git",
            "reponomics/reponomics-dashboard",
        )


def test_publish_commit_message_records_source_commit():
    message = publish_generated_repo._commit_message(
        "chore: publish generated template",
        "abc123",
    )

    assert message == "chore: publish generated template\n\nSource-Commit: abc123"
