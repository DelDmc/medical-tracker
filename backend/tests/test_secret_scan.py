import os
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_tc_sec_004_01_no_committed_file_contains_a_configured_secret():
    """TC-SEC-004-01 — No committed file contains a configured secret."""
    environ = dict(os.environ)
    # detect-secrets is installed next to the interpreter running the suite.
    environ["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{environ.get('PATH', '')}"

    result = subprocess.run(
        ["bash", str(REPOSITORY_ROOT / "scripts" / "secret-scan.sh")],
        cwd=REPOSITORY_ROOT,
        env=environ,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, result.stdout + result.stderr
