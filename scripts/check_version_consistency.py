#!/usr/bin/env python3
"""Fail if critical version references disagree with backend/version.py."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from version_utils import major_minor, read_version  # noqa: E402


@dataclass
class Mismatch:
    file: str
    expected: str
    found: str
    reason: str


def _fail(mismatches: list[Mismatch]) -> int:
    print('Version consistency check FAILED\n', file=sys.stderr)
    for item in mismatches:
        print(f'file: {item.file}', file=sys.stderr)
        print(f'expected version: {item.expected}', file=sys.stderr)
        print(f'found version: {item.found}', file=sys.stderr)
        print(f'reason: {item.reason}\n', file=sys.stderr)
    return 1


def check_version_py(version: str, mismatches: list[Mismatch]) -> None:
    text = (ROOT / 'backend/version.py').read_text(encoding='utf-8')
    if f"VERSION = '{version}'" not in text and f'VERSION = "{version}"' not in text:
        mismatches.append(Mismatch(
            'backend/version.py',
            version,
            'missing or mismatched VERSION constant',
            'VERSION must match __version__',
        ))


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_package_json(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    data = json.loads(path.read_text(encoding='utf-8'))
    found = data.get('version', '')
    if found != version:
        mismatches.append(Mismatch(_rel(path), version, found, 'package version field'))


def check_package_lock(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    data = json.loads(path.read_text(encoding='utf-8'))
    root_pkg = data.get('packages', {}).get('', {})
    found = root_pkg.get('version', data.get('version', ''))
    if found != version:
        mismatches.append(Mismatch(_rel(path), version, found, 'root package version'))


def check_dockerfile(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    text = path.read_text(encoding='utf-8')
    match = re.search(r'org\.opencontainers\.image\.version="([^"]+)"', text)
    found = match.group(1) if match else '<missing>'
    if found != version:
        mismatches.append(Mismatch(_rel(path), version, found, 'OCI image version label'))


def check_docker_workflow(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    text = path.read_text(encoding='utf-8')
    rel = _rel(path)
    mm = major_minor(version)

    uses_dynamic = (
        'id: appver' in text
        and 'steps.appver.outputs.version' in text
        and 'steps.appver.outputs.minor' in text
        and ('backend/version.py' in text or 'version_utils' in text)
    )
    if not uses_dynamic:
        mismatches.append(Mismatch(
            rel,
            version,
            'static or missing appver step',
            'Docker workflow must derive default-branch tags from backend/version.py',
        ))
        return

    for stale in re.findall(
        r'type=raw,value=(\d+\.\d+(?:\.\d+)?),enable=\{\{is_default_branch\}\}',
        text,
    ):
        if stale not in (mm, version):
            mismatches.append(Mismatch(
                rel,
                f'{mm} or {version}',
                stale,
                'stale hardcoded default-branch Docker tag',
            ))


def check_openapi_source(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    text = path.read_text(encoding='utf-8')
    if 'from version import __version__' not in text:
        mismatches.append(Mismatch(
            _rel(path),
            version,
            'no dynamic import',
            'OpenAPI spec must use __version__ from backend/version.py',
        ))


def previous_release_version(changelog_text: str, version: str) -> str | None:
    releases = re.findall(r'^## \[(\d+\.\d+\.\d+)\]', changelog_text, re.MULTILINE)
    if version not in releases:
        return None
    index = releases.index(version)
    if index + 1 < len(releases):
        return releases[index + 1]
    return None


def check_changelog(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    text = path.read_text(encoding='utf-8')
    rel = _rel(path)

    if f'## [{version}]' not in text:
        mismatches.append(Mismatch(rel, version, 'section missing', 'latest release section header'))

    unreleased = re.search(r'\[Unreleased\]:\s*(\S+)', text)
    expected_unreleased = f'compare/v{version}...main'
    if not unreleased:
        mismatches.append(Mismatch(rel, expected_unreleased, 'missing', '[Unreleased] compare link'))
    elif expected_unreleased not in unreleased.group(1):
        mismatches.append(Mismatch(
            rel,
            expected_unreleased,
            unreleased.group(1),
            '[Unreleased] compare link must start from current release tag',
        ))

    release_link = re.search(rf'\[{re.escape(version)}\]:\s*(\S+)', text)
    previous = previous_release_version(text, version)
    if not release_link:
        mismatches.append(Mismatch(rel, f'[{version}] link', 'missing', 'release compare link'))
    elif previous:
        expected_release = f'compare/v{previous}...v{version}'
        if expected_release not in release_link.group(1):
            mismatches.append(Mismatch(
                rel,
                expected_release,
                release_link.group(1),
                f'[{version}] compare link',
            ))


def check_readme(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    text = path.read_text(encoding='utf-8')
    rel = _rel(path)

    if version not in text:
        mismatches.append(Mismatch(rel, version, 'not mentioned', 'README must reference current release'))

    if re.search(r'(current|latest)\s+(release|version)[:\s`*]*4\.2\.0', text, re.IGNORECASE):
        mismatches.append(Mismatch(rel, version, '4.2.0 as current', 'README must not list 4.2.0 as current release'))

    if re.search(r'(current|latest)\s+(release|version)[:\s`*]*4\.2\.1(?!\d)', text, re.IGNORECASE):
        mismatches.append(Mismatch(rel, version, '4.2.1 as current', 'README must not list 4.2.1 as current release'))

    tags_section = re.search(r'\*\*Tags\*\*.*', text)
    if tags_section and version not in tags_section.group(0):
        mismatches.append(Mismatch(rel, version, tags_section.group(0), 'Docker Hub tags table missing current version'))


def check_docs_docker(path: Path, version: str, mismatches: list[Mismatch]) -> None:
    text = path.read_text(encoding='utf-8')
    rel = _rel(path)
    mm = major_minor(version)
    if version not in text:
        mismatches.append(Mismatch(rel, version, 'not mentioned', 'docs/docker.md must reference current release'))
    if mm not in text:
        mismatches.append(Mismatch(rel, mm, 'not mentioned', 'docs/docker.md must reference current minor tag'))


def main() -> int:
    try:
        version = read_version()
    except ValueError as exc:
        print(f'Version consistency check FAILED: {exc}', file=sys.stderr)
        return 1

    mismatches: list[Mismatch] = []

    check_version_py(version, mismatches)
    check_package_json(ROOT / 'frontend/package.json', version, mismatches)
    check_package_lock(ROOT / 'frontend/package-lock.json', version, mismatches)
    check_dockerfile(ROOT / 'Dockerfile', version, mismatches)
    check_docker_workflow(ROOT / '.github/workflows/docker.yml', version, mismatches)
    check_openapi_source(ROOT / 'backend/openapi/spec.py', version, mismatches)
    check_changelog(ROOT / 'CHANGELOG.md', version, mismatches)
    check_readme(ROOT / 'README.md', version, mismatches)
    check_docs_docker(ROOT / 'docs/docker.md', version, mismatches)

    if mismatches:
        return _fail(mismatches)

    print(f'Version consistency check passed: {version}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
