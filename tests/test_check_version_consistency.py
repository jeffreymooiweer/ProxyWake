"""Unit tests for version consistency checker logic."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from check_version_consistency import (  # noqa: E402
    Mismatch,
    check_changelog,
    check_docker_workflow,
    check_version_py,
    previous_release_version,
)


def test_previous_release_version_finds_prior_section():
    text = """## [Unreleased]

## [4.2.2] - 2026-07-06

## [4.2.1] - 2026-07-06
"""
    assert previous_release_version(text, '4.2.2') == '4.2.1'


def test_check_version_py_requires_version_constant():
    mismatches: list[Mismatch] = []
    check_version_py('9.9.9', mismatches)
    assert mismatches
    assert mismatches[0].reason == 'VERSION must match __version__'


def test_check_changelog_rejects_wrong_unreleased_link(tmp_path):
    changelog = tmp_path / 'CHANGELOG.md'
    changelog.write_text(
        '[Unreleased]: https://github.com/org/repo/compare/v4.2.1...main\n'
        '## [4.2.2] - 2026-07-06\n'
        '## [4.2.1] - 2026-07-06\n'
        '[4.2.2]: https://github.com/org/repo/compare/v4.2.1...v4.2.2\n',
        encoding='utf-8',
    )
    mismatches: list[Mismatch] = []
    check_changelog(changelog, '4.2.2', mismatches)
    assert any('Unreleased' in item.reason for item in mismatches)


def test_check_docker_workflow_rejects_stale_hardcoded_tag(tmp_path):
    workflow = tmp_path / 'docker.yml'
    workflow.write_text(
        'id: appver\n'
        'steps.appver.outputs.version\n'
        'steps.appver.outputs.minor\n'
        'version_utils\n'
        'type=raw,value=4.2.0,enable={{is_default_branch}}\n',
        encoding='utf-8',
    )
    mismatches: list[Mismatch] = []
    check_docker_workflow(workflow, '4.2.2', mismatches)
    assert any('stale hardcoded' in item.reason for item in mismatches)
