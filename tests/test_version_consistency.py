"""Ensure critical version files stay aligned with backend/version.py."""

import subprocess
import sys
from pathlib import Path


def test_version_consistency_script_passes():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(root / 'scripts' / 'check_version_consistency.py')],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
