"""Security scanning tests using Bandit."""

import subprocess


def test_bandit_security_scan():
    """Run Bandit security scanner over the source tree."""
    result = subprocess.run(
        ["bandit", "-q", "-r", "src"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
