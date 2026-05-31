"""Tests for generated Reponomics dashboard repository outputs."""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_template
import publish_generated_repo
import sync_action_release
import template_consumer_e2e
import verify_workflow_classification


ACTION_YML_FIXTURE = """
inputs:
  mode:
    description: "Runtime mode: collect, publish, rotate-key, incident-reset, or docs-sync."
  allow-docs-sync:
    description: "Optional managed docs sync override."
outputs:
  docs-sync-state:
    value: ${{ steps.runtime.outputs.docs-sync-state }}
  docs-action-version:
    value: ${{ steps.runtime.outputs.docs-action-version }}
  docs-updated-at:
    value: ${{ steps.runtime.outputs.docs-updated-at }}
"""


def test_template_manifest_includes_thin_template_surface(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    required = [
        ".github/workflows/collect.yml.disabled",
        ".github/workflows/incident-sentinel.yml.disabled",
        ".github/workflows/keepalive.yml.disabled",
        ".github/workflows/publish.yml.disabled",
        ".github/workflows/setup.yml",
        ".github/workflows/rotate-key.yml",
        "README.md",
        "config.yaml",
        "config.example.yaml",
        "docs/FAQ.md",
        "docs/PROVENANCE.md",
        "docs/README.md",
        "docs/SECURE_DASHBOARD_KEY.md",
        "docs/TRUST_BOUNDARY.md",
        "docs/architecture/PRIVACY_CONFIGURATION_MATRIX.md",
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
        "template",
        "template-action-release.yml",
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
    release = sync_action_release.load_manifest()

    workflows = output / ".github" / "workflows"
    collect = (workflows / "collect.yml.disabled").read_text(encoding="utf-8")
    sentinel = (workflows / "incident-sentinel.yml.disabled").read_text(encoding="utf-8")
    keepalive = (workflows / "keepalive.yml.disabled").read_text(encoding="utf-8")
    publish = (workflows / "publish.yml.disabled").read_text(encoding="utf-8")
    setup = (workflows / "setup.yml").read_text(encoding="utf-8")
    rotate = (workflows / "rotate-key.yml").read_text(encoding="utf-8")

    action_ref = f"uses: {release.repository}@{release.tag}"
    action_ref_env = f'REPONOMICS_ACTION_REF: "{release.tag}"'
    action_sha_env = f'REPONOMICS_ACTION_SHA: "{release.target_commitish}"'
    html_env = 'GENERATE_HTML_DASHBOARD: "false"'
    assert "docs-sync:" in collect
    assert "mode: docs-sync" in collect
    assert "github-token: ${{ github.token }}" in collect
    assert "allow-docs-sync" not in collect
    assert action_ref in collect
    assert action_ref_env in collect
    assert action_sha_env in collect
    assert html_env in collect
    assert "reponomics-collect-provenance" in collect
    assert '"generate_html_dashboard": os.environ["GENERATE_HTML_DASHBOARD"]' in collect
    assert "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in collect
    assert "source_sha" in publish
    assert "workflow_run_id" in publish
    assert "action_sha" in publish
    assert (
        "EXPECTED_WORKFLOW_RUN_ID: ${{ github.event.workflow_run.id || '' }}"
        in publish
    )
    assert "resolve_action_ref(expected_repository, action_ref)" in publish
    assert "Publish stopped: action release provenance is inconsistent" in publish
    assert "Publish stopped: collect provenance does not match this publish trigger" in publish
    assert "Do not rerun publish. Run `Collect Reponomics Data` again" in publish
    assert "Repair the generated workflow action metadata" in publish
    assert "generate_html_dashboard" in publish
    assert "uses: ./reponomics-dashboard-action" in publish
    assert "if: steps.provenance.outputs.generate_html_dashboard == 'true'" in publish
    assert "Render README and downloadable dashboard without Pages deployment" in publish
    assert "Upload plain downloadable dashboard" in publish
    assert "Upload encrypted downloadable dashboard" in publish
    assert "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405" in publish
    assert "actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c" in publish
    assert "repository: ${{ steps.provenance.outputs.action_repository }}" in publish
    assert "ref: ${{ steps.provenance.outputs.action_sha }}" in publish
    assert "mode: docs-sync" not in publish
    assert "allow-docs-sync" not in publish
    assert html_env in publish
    assert action_ref_env in publish
    assert action_sha_env in publish
    assert action_ref not in setup
    assert action_ref in rotate
    assert "python scripts/" not in collect
    assert "python scripts/" not in sentinel
    assert "python scripts/" not in keepalive
    assert "python scripts/" not in publish
    assert "python scripts/" not in setup
    assert "python scripts/" not in rotate
    assert "mode: collect" in collect
    assert 'USE_GITHUB_APP: "false"' in collect
    assert "actions/create-github-app-token@bcd2ba49218906704ab6c1aa796996da409d3eb1" in collect
    assert "app-id: ${{ vars.COLLECTION_APP_ID || secrets.COLLECTION_APP_ID }}" in collect
    assert "use-github-app: ${{ env.USE_GITHUB_APP }}" in collect
    assert "mode: publish" in publish
    assert "workflow_run:" in publish
    assert "COLLECTION_TOKEN" not in keepalive
    assert "DASHBOARD_SECRET_DO_NOT_REPLACE" not in keepalive
    assert "60 days without repository activity" in keepalive


def test_setup_workflow_resolves_privacy_modes():
    setup = Path("template/.github/workflows/setup.yml").read_text(encoding="utf-8")

    for mode in ("strong", "casual", "plain"):
        assert re.search(rf"^\s+- {mode}$", setup, flags=re.MULTILINE)

    assert "generate_html_dashboard:" in setup
    assert 'description: "Publish hosted HTML dashboard after collection"' in setup
    assert "generate_readme:" in setup
    assert 'description: "Generate README after collection (private repositories only)"' in setup
    assert "use_github_app:" in setup
    assert 'description: "Advanced collection auth: use a user-owned GitHub App installation token"' in setup
    assert "publish_dashboard:" not in setup
    assert "commit_readme:" not in setup
    assert "commit_readme_snapshot:" not in setup
    assert "PUBLISH_TO_PAGES" not in setup
    assert "PUBLISH_README" not in setup
    assert "COMMIT_README_SNAPSHOT" not in setup
    assert 'echo "PRIVACY_MODE=$resolved_privacy_mode"' in setup
    assert 'echo "GENERATE_HTML_DASHBOARD=$GENERATE_HTML_DASHBOARD"' in setup
    assert 'echo "GENERATE_README=$GENERATE_README"' in setup
    assert '"GENERATE_HTML_DASHBOARD": os.environ["GENERATE_HTML_DASHBOARD"]' in setup
    assert '"GENERATE_README": os.environ["GENERATE_README"]' in setup
    assert 'echo "USE_GITHUB_APP=$USE_GITHUB_APP"' in setup
    assert "README dashboard generation is only supported for private repositories." in setup
    assert "cat > README.md <<'MD'" in setup
    assert "This repository was generated from the [Reponomics Dashboard template repo]" in setup
    assert "allow_docs_sync: false" in setup
    assert "Managed docs sync" in setup
    assert "git add -A .github/workflows README.md" in setup
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
    assert "DASHBOARD_NEXT_SECRET" not in setup
    assert 'enable_workflow ".github/workflows/incident-sentinel.yml"' in setup
    assert 'enable_workflow ".github/workflows/keepalive.yml"' in setup
    assert "Scheduled workflow keepalive" in setup
    assert "60 days without repository activity" in setup
    assert "token: ${{ secrets.COLLECTION_TOKEN" not in setup
    assert "personal-access-tokens/new" in setup
    assert "name=COLLECTION_TOKEN" in setup
    assert "name=Reponomics%20Collection%20Token" not in setup
    assert "administration=read" in setup
    assert "target_name=$GITHUB_REPOSITORY_OWNER" in setup
    assert "All repositories" in setup
    assert "Only selected repositories" in setup
    assert "keep \\`config.yaml\\` within" in setup
    assert "COLLECTION_APP_PRIVATE_KEY" in setup
    assert "COLLECTION_APP_ID" in setup
    assert '"USE_GITHUB_APP": os.environ["USE_GITHUB_APP"]' in setup
    assert "docs/SECURE_DASHBOARD_KEY.md" in setup
    assert "docs/architecture/PRIVACY_CONFIGURATION_MATRIX.md" in setup
    assert "not strong enough for \\`privacy_mode=strong\\`" in setup
    assert "Casual privacy mode selected" not in setup
    casual_length_check = (
        '${#DASHBOARD_SECRET_DO_NOT_REPLACE}" -lt 40 ] && [ "$PRIVACY_MODE" = "casual"'
    )
    assert casual_length_check not in setup
    assert "Manual GitHub Pages step" in setup
    assert '[ "$GENERATE_HTML_DASHBOARD" = "true" ] && [ "$PRIVACY_MODE" != "plain" ]' in setup
    assert "Collection auth mode" in setup
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
        assert "supports one collection credential" in text
        assert "Fine-grained personal access tokens are scoped to one GitHub resource owner" in text
        assert re.search(r"multiple users or\s+organizations", text)
        assert "classic PAT" in text
        assert re.search(r"`repo`\s+scope", text)


def test_config_documents_managed_docs_opt_out():
    config_example = Path("config.example.yaml").read_text(encoding="utf-8")
    config = Path("config.yaml").read_text(encoding="utf-8")

    for text in (config_example, config):
        assert "allow_docs_sync: true" in text
        assert "docs/reponomics/" in text


def test_action_release_manifest_and_metadata_contract():
    release = sync_action_release.load_manifest()

    assert release.repository == sync_action_release.ACTION_REPOSITORY
    assert re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", release.tag)
    assert re.fullmatch(r"[0-9a-f]{40}", release.target_commitish)
    sync_action_release.validate_action_metadata(ACTION_YML_FIXTURE)


def test_action_release_sync_workflow_can_update_existing_branch():
    workflow = Path(".github/workflows/dev-sync-action-release.yml").read_text(
        encoding="utf-8"
    )

    assert 'git ls-remote --exit-code --heads origin "$branch"' in workflow
    assert (
        'git fetch --depth=1 origin "${remote_ref}:refs/remotes/origin/${branch}"'
        in workflow
    )
    assert (
        'git push --force-with-lease="${remote_ref}:${expected}" '
        'origin "HEAD:${remote_ref}"'
    ) in workflow
    assert 'git push origin "HEAD:${remote_ref}"' in workflow


def test_action_release_sync_rewrites_refs_and_status(tmp_path):
    release = sync_action_release.ActionRelease(
        repository=sync_action_release.ACTION_REPOSITORY,
        tag="v0.16.0",
        target_commitish="a" * 40,
        release_url="https://github.com/reponomics/reponomics-dashboard-action/releases/tag/v0.16.0",
        published_at="2026-05-31T05:19:33Z",
    )
    old_tag = "v0." + "15.0"
    readme = tmp_path / "README.md"
    readme.write_text(
        f"Status: current for action `{old_tag}`.\n"
        f"uses: reponomics/reponomics-dashboard-action@{old_tag}\n"
        f'  REPONOMICS_ACTION_REF: "{old_tag}"\n'
        f'  REPONOMICS_ACTION_SHA: "{"b" * 40}"\n',
        encoding="utf-8",
    )

    sync_action_release.sync_release(tmp_path, release, ACTION_YML_FIXTURE)

    assert old_tag not in readme.read_text(encoding="utf-8")
    assert "reponomics-dashboard-action@v0.16.0" in readme.read_text(encoding="utf-8")
    assert 'REPONOMICS_ACTION_REF: "v0.16.0"' in readme.read_text(encoding="utf-8")
    assert f'REPONOMICS_ACTION_SHA: "{release.target_commitish}"' in readme.read_text(
        encoding="utf-8"
    )
    assert sync_action_release.load_manifest(tmp_path).tag == "v0.16.0"


def test_action_release_verify_rejects_stale_refs(tmp_path):
    release = sync_action_release.ActionRelease(
        repository=sync_action_release.ACTION_REPOSITORY,
        tag="v0.16.0",
        target_commitish="a" * 40,
        release_url="https://github.com/reponomics/reponomics-dashboard-action/releases/tag/v0.16.0",
        published_at="2026-05-31T05:19:33Z",
    )
    sync_action_release.write_manifest(release, tmp_path)
    old_tag = "v0." + "15.0"
    (tmp_path / "README.md").write_text(
        f"uses: reponomics/reponomics-dashboard-action@{old_tag}\n"
        f'  REPONOMICS_ACTION_REF: "{old_tag}"\n'
        f'  REPONOMICS_ACTION_SHA: "{"b" * 40}"\n',
        encoding="utf-8",
    )

    with pytest.raises(sync_action_release.ActionReleaseError):
        sync_action_release.verify_release(tmp_path, release, ACTION_YML_FIXTURE)


def test_workflow_classification_contract():
    verify_workflow_classification.verify()


def test_template_consumer_e2e_absolutizes_cwd_relative_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    action_python = Path("action-runtime/venv/bin/python")

    assert template_consumer_e2e._absolute_path(action_python) == tmp_path / action_python


def test_template_docs_do_not_reference_old_brand_or_maintenance_docs(tmp_path):
    output = tmp_path / "template"

    build_template.build_template(output)

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output.rglob("*")
        if path.is_file() and path.suffix in {"", ".md", ".yml", ".yaml", ".html"}
    )
    assert "github-traffic-report" not in text
    assert "GitHub Traffic Report" not in text
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
