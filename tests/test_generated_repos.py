"""Tests for generated Reponomics dashboard repository outputs."""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_template
import publish_generated_repo
import verify_workflow_classification


def test_template_manifest_includes_thin_template_surface(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    required = [
        ".github/workflows/collect.yml.disabled",
        ".github/workflows/incident-sentinel.yml.disabled",
        ".github/workflows/publish.yml.disabled",
        ".github/workflows/setup.yml",
        ".github/workflows/rotate-key.yml",
        "README.md",
        "config.yaml",
        "config.example.yaml",
        "docs/README.md",
        "docs/SECURE_DASHBOARD_KEY.md",
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
        "docs/archive",
        "docs/adr",
    ]
    for relative_path in forbidden:
        assert not (output / relative_path).exists()


def test_template_workflows_delegate_to_reponomics_action(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    workflows = output / ".github" / "workflows"
    collect = (workflows / "collect.yml.disabled").read_text(encoding="utf-8")
    sentinel = (workflows / "incident-sentinel.yml.disabled").read_text(encoding="utf-8")
    publish = (workflows / "publish.yml.disabled").read_text(encoding="utf-8")
    setup = (workflows / "setup.yml").read_text(encoding="utf-8")
    rotate = (workflows / "rotate-key.yml").read_text(encoding="utf-8")

    action_ref = "uses: reponomics/reponomics-dashboard-action@v0.8.0"
    assert action_ref in collect
    assert action_ref in publish
    assert action_ref not in setup
    assert action_ref in rotate
    assert "python scripts/" not in collect
    assert "python scripts/" not in sentinel
    assert "python scripts/" not in publish
    assert "python scripts/" not in setup
    assert "python scripts/" not in rotate
    assert "mode: collect" in collect
    assert "mode: publish" in publish
    assert "workflow_run:" in publish


def test_setup_workflow_resolves_privacy_modes():
    setup = Path(".github/workflows/setup.yml").read_text(encoding="utf-8")

    for mode in ("strong", "casual", "plain"):
        assert re.search(rf"^\s+- {mode}$", setup, flags=re.MULTILINE)

    assert "generate_html_dashboard:" in setup
    assert 'description: "Generate HTML dashboard after collection"' in setup
    assert "generate_readme:" in setup
    assert 'description: "Generate README after collection"' in setup
    assert "publish_dashboard:" not in setup
    assert "commit_readme:" not in setup
    assert "commit_readme_snapshot:" not in setup
    assert "PUBLISH_TO_PAGES" not in setup
    assert "PUBLISH_README" not in setup
    assert "COMMIT_README_SNAPSHOT" not in setup
    assert 'echo "PRIVACY_MODE=$privacy_mode"' in setup
    assert 'echo "COMMIT_OUTPUTS=$GENERATE_README"' in setup
    assert 'RETENTION_DAYS: "90"' in setup
    assert "retention_days:" not in setup
    assert '"OUTAGE_RETENTION_DAYS": os.environ["RETENTION_DAYS"]' in setup
    assert "privacy_mode=plain" in setup
    assert "is only supported for private repositories." in setup
    assert "privacy_mode=strong" in setup
    assert "privacy_mode=casual" in setup
    assert re.search(r"^permissions:\n  contents: read$", setup, flags=re.MULTILINE)
    assert re.search(r"^\s+permissions:\n\s+contents: write$", setup, flags=re.MULTILINE)
    assert "actions: write" not in setup
    assert "TRAFFIC_DASHBOARD_NEXT_SECRET" not in setup
    assert 'enable_workflow ".github/workflows/incident-sentinel.yml"' in setup
    assert "token: ${{ secrets.TRAFFIC_TOKEN" not in setup
    assert "personal-access-tokens/new" in setup
    assert "administration=read" in setup
    assert "target_name=$GITHUB_REPOSITORY_OWNER" in setup
    assert "All repositories" in setup
    assert "Only selected repositories" in setup
    assert "keep \\`config.yaml\\` within" in setup
    assert "docs/SECURE_DASHBOARD_KEY.md" in setup
    assert "docs/architecture/PRIVACY_CONFIGURATION_MATRIX.md" in setup
    assert "not strong enough for \\`privacy_mode=strong\\`" in setup
    assert "Casual privacy mode selected" not in setup
    casual_length_check = (
        '${#TRAFFIC_DASHBOARD_SECRET}" -lt 40 ] && [ "$PRIVACY_MODE" = "casual"'
    )
    assert casual_length_check not in setup
    assert "Manual GitHub Pages step" in setup
    assert "Settings -> Pages" in setup
    assert "skip them" in setup
    assert "repos/$GITHUB_REPOSITORY/pages" not in setup
    assert "PAGES_PUBLICATION" not in setup


def test_docs_explain_multi_owner_token_fallback():
    readme = Path("README.md").read_text(encoding="utf-8")
    docs = Path("docs/README.md").read_text(encoding="utf-8")

    assert "Token Scope And Repository Owners" in readme
    assert "before choosing a token" in readme
    assert "Repository entries use full `owner/repo` names" in readme

    for text in (readme, docs):
        assert "Fine-grained personal access tokens are scoped to one GitHub resource owner" in text
        assert re.search(r"multiple users or\s+organizations", text)
        assert "classic PAT" in text
        assert re.search(r"`repo`\s+scope", text)


def test_workflow_classification_contract():
    verify_workflow_classification.verify()


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
