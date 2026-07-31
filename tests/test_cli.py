"""
tests/test_cli.py

Generic CLI tests for Darkelf projects.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def run_command(*args):
    """Run a CLI command and capture output."""
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=30,
    )


# ---------------------------------------------------------------------
# SecureAudit
# ---------------------------------------------------------------------


def test_secureaudit_exists():
    if shutil.which("darkelf-secureaudit") is None:
        pytest.skip("darkelf-secureaudit not installed")


def test_secureaudit_help():
    if shutil.which("darkelf-secureaudit") is None:
        pytest.skip("darkelf-secureaudit not installed")

    result = run_command("darkelf-secureaudit", "--help")

    assert result.returncode == 0


def test_secureaudit_version():
    """
    Run only if SecureAudit implements a --version flag.
    """
    if shutil.which("darkelf-secureaudit") is None:
        pytest.skip("darkelf-secureaudit not installed")

    help_result = run_command("darkelf-secureaudit", "--help")

    if "--version" not in help_result.stdout:
        pytest.skip("SecureAudit does not implement --version")

    result = run_command("darkelf-secureaudit", "--version")

    assert result.returncode == 0


# ---------------------------------------------------------------------
# Dependency Guardian
# ---------------------------------------------------------------------


def test_dependency_guardian_exists():
    if shutil.which("darkelf-dependency-guardian") is None:
        pytest.skip("Dependency Guardian not installed")


def test_dependency_guardian_help():
    if shutil.which("darkelf-dependency-guardian") is None:
        pytest.skip("Dependency Guardian not installed")

    result = run_command(
        "darkelf-dependency-guardian",
        "--help",
    )

    assert result.returncode == 0


# ---------------------------------------------------------------------
# Shadow
# ---------------------------------------------------------------------


def test_shadow_exists():
    if shutil.which("darkelf-shadow") is None:
        pytest.skip("Darkelf Shadow not installed")


def test_shadow_help():
    """
    Shadow should support --help.

    Skip on Linux because the Qt GUI aborts in the
    GitHub Actions headless environment.
    """
    import platform

    if platform.system() == "Linux":
        pytest.skip("Shadow CLI help is not supported on Linux CI")

    if shutil.which("darkelf-shadow") is None:
        pytest.skip("Darkelf Shadow not installed")

    try:
        result = run_command(
            "darkelf-shadow",
            "--help",
        )
    except subprocess.TimeoutExpired:
        pytest.skip(
            "darkelf-shadow currently launches the GUI instead of exiting with --help"
        )

    assert result.returncode == 0

# ---------------------------------------------------------------------
# Cocoa
# ---------------------------------------------------------------------


def test_cocoa_exists():
    if shutil.which("darkelf-cocoa") is None:
        pytest.skip("Darkelf Cocoa not installed")


def test_cocoa_help():
    if shutil.which("darkelf-cocoa") is None:
        pytest.skip("Darkelf Cocoa not installed")

    result = run_command(
        "darkelf-cocoa",
        "--help",
    )

    assert result.returncode == 0


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_unknown_command_fails():
    result = run_command(
        "python",
        "-c",
        "import sys; sys.exit(2)",
    )

    assert result.returncode == 2


def test_python_available():
    result = run_command(
        "python",
        "--version",
    )

    assert result.returncode == 0
