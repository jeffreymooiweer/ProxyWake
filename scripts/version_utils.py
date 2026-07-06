"""Shared helpers for ProxyWake version synchronization and checks."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / 'backend' / 'version.py'


def read_version(path: Path | None = None) -> str:
    text = (path or VERSION_FILE).read_text(encoding='utf-8')
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
    if not match:
        raise ValueError(f'Could not parse __version__ from {path or VERSION_FILE}')
    version = match.group(1)
    version_const = re.search(r"^VERSION\s*=\s*['\"]([^'\"]+)['\"]", text, re.MULTILINE)
    if version_const and version_const.group(1) != version:
        raise ValueError(
            f'VERSION ({version_const.group(1)}) does not match __version__ ({version})'
        )
    return version


def major_minor(version: str) -> str:
    parts = version.split('.')
    return '.'.join(parts[:2]) if len(parts) >= 2 else version
