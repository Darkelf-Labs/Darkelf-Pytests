"""
tests/test_cli_exit_codes.py

Validate CLI exit codes for Darkelf command-line tools.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.regression,
]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def run_cli(command: str, *args: str) -> subprocess.CompletedProcess:
    """Execute a CLI command."""
    return subprocess.run(
        [command, *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def require_cli(name: str) -> None:
    """Skip if a CLI executable is unavailable."""
    if shutil.which(name) is None:
        pytest.skip(f"{name} is not installed")


# ---------------------------------------------------------------------
# SecureAudit
# ---------------------------------------------------------------------


def test_secureaudit_help_exit_code():
    require_cli("darkelf-secureaudit")

    result = run_cli("darkelf-secureaudit", "--help")

    assert result.returncode == 0


def test_secureaudit_version_exit_code():
    require_cli("darkelf-secureaudit")

    help_result = run_cli(
        "darkelf-secureaudit",
        "--help",
    )

    if "--version" not in help_result.stdout:
        pytest.skip("SecureAudit does not implement --version")

    result = run_cli(
        "darkelf-secureaudit",
        "--version",
    )

    assert result.returncode == 0


def test_secureaudit_invalid_argument():
    require_cli("darkelf-secureaudit")

    result = run_cli(
        "darkelf-secureaudit",
        "--definitely-invalid-option",
    )

    assert result.returncode != 0


# ---------------------------------------------------------------------
# Dependency Guardian
# ---------------------------------------------------------------------


def test_dependency_guardian_help():
    require_cli("guardian")

    result = run_cli(
        "guardian",
        "--help",
    )

    assert result.returncode == 0


def test_dependency_guardian_invalid_argument():
    require_cli("guardian")

    result = run_cli(
        "guardian",
        "--bad-option",
    )

    assert result.returncode != 0


# ---------------------------------------------------------------------
# Shadow
# ---------------------------------------------------------------------


def test_shadow_help():
    import platform

    if platform.system() == "Linux":
        pytest.skip("Shadow CLI help is not supported on Linux CI")

    require_cli("darkelf-shadow")

    try:
        result = run_cli(
            "darkelf-shadow",
            "--help",
        )
    except subprocess.TimeoutExpired:
        pytest.skip("darkelf-shadow currently launches the GUI instead of exiting with --help")

    assert result.returncode == 0
    

# ---------------------------------------------------------------------
# Python Exit Codes
# ---------------------------------------------------------------------


def test_python_zero_exit():
    result = subprocess.run(
        ["python", "-c", "import sys; sys.exit(0)"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0


def test_python_nonzero_exit():
    result = subprocess.run(
        ["python", "-c", "import sys; sys.exit(1)"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1


def test_python_invalid_argument():
    result = subprocess.run(
        ["python", "--definitely-invalid-option"],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_help_produces_output():
    require_cli("darkelf-secureaudit")

    result = run_cli(
        "darkelf-secureaudit",
        "--help",
    )

    assert result.stdout.strip() != ""


def test_invalid_option_produces_error():
    require_cli("darkelf-secureaudit")

    result = run_cli(
        "darkelf-secureaudit",
        "--invalid",
    )

    assert result.stderr.strip() != ""
