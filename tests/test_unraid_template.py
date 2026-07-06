"""Tests for the Unraid Community Applications template."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))

from validate_unraid_template import TEMPLATE_PATH, validate_template  # noqa: E402


def test_unraid_template_validates():
    validate_template(TEMPLATE_PATH)


def test_unraid_template_exists():
    assert TEMPLATE_PATH.is_file()


def test_unraid_icon_exists():
    icon_path = Path(__file__).resolve().parent.parent / 'unraid' / 'icons' / 'proxywake.png'
    assert icon_path.is_file()
    assert icon_path.stat().st_size > 0
