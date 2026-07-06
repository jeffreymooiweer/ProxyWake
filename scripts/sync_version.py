#!/usr/bin/env python3
"""Synchronize ProxyWake version from backend/version.py to all consumer files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from version_utils import major_minor, read_version  # noqa: E402

VERSION_FILE = ROOT / 'backend' / 'version.py'


def update_package_json(path: Path, version: str) -> bool:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('version') == version:
        return False
    data['version'] = version
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return True


def update_package_lock(path: Path, version: str) -> bool:
    data = json.loads(path.read_text(encoding='utf-8'))
    changed = False
    if data.get('version') != version:
        data['version'] = version
        changed = True
    packages = data.get('packages', {})
    root = packages.get('', {})
    if root.get('version') != version:
        root['version'] = version
        packages[''] = root
        data['packages'] = packages
        changed = True
    if changed:
        path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return changed


def update_dockerfile(path: Path, version: str) -> bool:
    text = path.read_text(encoding='utf-8')
    new_text, count = re.subn(
        r'org\.opencontainers\.image\.version="[^"]*"',
        f'org.opencontainers.image.version="{version}"',
        text,
        count=1,
    )
    if count == 0:
        raise SystemExit(f'OCI version label not found in {path}')
    if new_text == text:
        return False
    path.write_text(new_text, encoding='utf-8')
    return True


def update_version_py_version_constant(path: Path, version: str) -> bool:
    text = path.read_text(encoding='utf-8')
    new_text, count = re.subn(
        r"^VERSION\s*=\s*['\"][^'\"]+['\"]",
        f"VERSION = '{version}'",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        if f"VERSION = '{version}'" in text:
            return False
        raise SystemExit(f'VERSION constant not found in {path}')
    if new_text == text:
        return False
    path.write_text(new_text, encoding='utf-8')
    return True


def update_docker_workflow_description(path: Path, version: str) -> bool:
    text = path.read_text(encoding='utf-8')
    new_text, count = re.subn(
        r"description: 'Extra Docker tag \(e\.g\. [^']+\)'",
        f"description: 'Extra Docker tag (e.g. {version})'",
        text,
        count=1,
    )
    if new_text == text:
        return False
    path.write_text(new_text, encoding='utf-8')
    return True


def update_docs_docker_tags(path: Path, version: str) -> bool:
    text = path.read_text(encoding='utf-8')
    mm = major_minor(version)
    new_line = f"| Tags | `latest`, `{mm}`, `{version}` (see [CHANGELOG](../CHANGELOG.md)) |"
    new_text, count = re.subn(
        r'\| Tags \| `latest`, `[^`]+`, `[^`]+` \(see \[CHANGELOG\]\(\.\./CHANGELOG\.md\)\) \|',
        new_line,
        text,
        count=1,
    )
    if count == 0 or new_text == text:
        return False
    path.write_text(new_text, encoding='utf-8')
    return True


def main() -> int:
    version = read_version(VERSION_FILE)
    updates: list[str] = []

    targets = [
        ('frontend/package.json', lambda p: update_package_json(p, version)),
        ('frontend/package-lock.json', lambda p: update_package_lock(p, version)),
        ('Dockerfile', lambda p: update_dockerfile(p, version)),
        ('.github/workflows/docker.yml', lambda p: update_docker_workflow_description(p, version)),
        ('docs/docker.md', lambda p: update_docs_docker_tags(p, version)),
    ]

    for rel, updater in targets:
        path = ROOT / rel
        if not path.exists():
            print(f'Skip missing {rel}', file=sys.stderr)
            continue
        if updater(path):
            updates.append(rel)

    print(f'Version source: backend/version.py → {version}')
    if updates:
        print('Updated:')
        for name in updates:
            print(f'  - {name}')
    else:
        print('All consumer files already match.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
