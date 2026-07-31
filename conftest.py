"""
conftest.py

Shared pytest fixtures for the Darkelf Labs test suite.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------


@pytest.fixture(scope="session")
def python_version():
    """Return the running Python version."""
    return sys.version_info


@pytest.fixture(scope="session")
def platform_name():
    """Return the current operating system."""
    return platform.system()


@pytest.fixture(scope="session")
def project_root():
    """Return the root directory of the test repository."""
    return Path(__file__).resolve().parent


@pytest.fixture(scope="session")
def tests_root(project_root):
    """Return the tests directory."""
    return project_root / "tests"


@pytest.fixture(scope="session")
def sample_data(tests_root):
    """Return the sample data directory."""
    return tests_root / "data"


# ---------------------------------------------------------------------
# Feature Detection
# ---------------------------------------------------------------------


@pytest.fixture(scope="session")
def is_macos():
    return platform.system() == "Darwin"


@pytest.fixture(scope="session")
def is_linux():
    return platform.system() == "Linux"


@pytest.fixture(scope="session")
def is_windows():
    return platform.system() == "Windows"


# ---------------------------------------------------------------------
# Optional Dependencies
# ---------------------------------------------------------------------


@pytest.fixture(scope="session")
def has_pyobjc():
    try:
        import AppKit  # noqa: F401

        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def has_qt():
    try:
        import PySide6  # noqa: F401

        return True
    except Exception:
        return False


# ---------------------------------------------------------------------
# Common Assertions
# ---------------------------------------------------------------------


@pytest.fixture
def no_exception():
    """
    Simple helper fixture.

    Example:

        def test_example(no_exception):
            with no_exception:
                do_something()
    """

    from contextlib import nullcontext

    return nullcontext()
