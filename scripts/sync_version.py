#!/usr/bin/env python3
"""Synchronize ProxyWake version from backend/version.py to all consumer files."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / 'backend' / 'version.py'


def read_version() -> str:
    text = VERSION_FILE.read_text(encoding='utf-8')
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
    if not match:
        raise SystemExit(f'Could not parse __version__ from {VERSION_FILE}')
    return match.group(1)


def major_minor(version: str) -> str:
    parts = version.split('.')
    return '.'.join(parts[:2]) if len(parts) >= 2 else version


def update_package_json(path: Path, version: str) -> bool:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('version') == version:
        return False
    data['version'] = version
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return True


def update_package_lock(path: Path, version: str) -> bool:
    text = path.read_text(encoding='utf-8')
    data = json.loads(text)
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


def update_docker_workflow(path: Path, version: str) -> bool:
    text = path.read_text(encoding='utf-8')
    mm = major_minor(version)
    changed = False

    new_text, count = re.subn(
        r"description: 'Extra Docker tag \(e\.g\. [^']+\)'",
        f"description: 'Extra Docker tag (e.g. {version})'",
        text,
        count=1,
    )
    if count:
        changed = changed or new_text != text
        text = new_text

    pattern = re.compile(
        r'type=raw,value=(\d+\.\d+(?:\.\d+)?),enable=\{\{is_default_branch\}\}'
    )
    replacements = {mm: None, version: None}
    for match in pattern.finditer(text):
        replacements[match.group(1)] = match.group(0)

    for tag, old_line in list(replacements.items()):
        if tag in (mm, version):
            continue
        if old_line is None:
            continue
        if tag == mm and replacements[mm] is None:
            text = text.replace(old_line, f'type=raw,value={mm},enable={{{{is_default_branch}}}}', 1)
            changed = True
        elif tag == version and replacements[version] is None:
            text = text.replace(old_line, f'type=raw,value={version},enable={{{{is_default_branch}}}}', 1)
            changed = True

    # Ensure both minor and full semver tags exist on default branch
    tags_block = 'type=raw,value=latest,enable={{is_default_branch}}'
    minor_line = f'type=raw,value={mm},enable={{{{is_default_branch}}}}'
    full_line = f'type=raw,value={version},enable={{{{is_default_branch}}}}'
    if minor_line not in text:
        text = text.replace(
            tags_block,
            f'{tags_block}\n            {minor_line}',
            1,
        )
        changed = True
    if full_line not in text:
        text = text.replace(
            minor_line,
            f'{minor_line}\n            {full_line}',
            1,
        )
        changed = True

    if changed:
        path.write_text(text, encoding='utf-8')
    return changed


def main() -> int:
    version = read_version()
    updates: list[str] = []

    targets = [
        ('frontend/package.json', lambda p: update_package_json(p, version)),
        ('frontend/package-lock.json', lambda p: update_package_lock(p, version)),
        ('Dockerfile', lambda p: update_dockerfile(p, version)),
        ('.github/workflows/docker.yml', lambda p: update_docker_workflow(p, version)),
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
