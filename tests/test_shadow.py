"""
tests/test_shadow.py

Tests for Darkelf Shadow.
Designed to work both locally and in GitHub Actions.
"""

from __future__ import annotations

import platform
import sys
from importlib.util import find_spec
from pathlib import Path

import pytest

pytestmark = pytest.mark.shadow

HAS_SHADOW = find_spec("darkelf_shadow") is not None


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------


def test_python_version():
    """Shadow requires Python 3.11+."""
    assert sys.version_info >= (3, 11)


def test_platform_supported():
    """Shadow supports common desktop platforms."""
    assert platform.system() in {
        "Darwin",
        "Linux",
        "Windows",
    }


def test_pyside6_available():
    """PySide6 should be importable if installed."""
    try:
        import PySide6  # noqa: F401
    except ImportError:
        pytest.skip("PySide6 not installed")


def test_qtwebengine_available():
    """QtWebEngine should be available if PySide6 is installed."""
    try:
        from PySide6.QtWebEngineCore import QWebEngineProfile  # noqa: F401
    except ImportError:
        pytest.skip("QtWebEngine not available")


# ---------------------------------------------------------------------
# Package Tests
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_package_import():
    """Package imports successfully."""
    import darkelf_shadow  # noqa: F401


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_main_module_import():
    """Main module imports successfully."""
    from darkelf_shadow import main  # noqa: F401


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_package_path_exists():
    """Installed package has a valid filesystem path."""
    import darkelf_shadow

    assert Path(darkelf_shadow.__file__).exists()


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_cli_entrypoint_exists():
    """CLI entrypoint exists."""
    from darkelf_shadow.main import main

    assert callable(main)


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_package_has_version():
    """Package exposes a version string if available."""
    import darkelf_shadow

    version = getattr(darkelf_shadow, "__version__", None)

    if version is not None:
        assert isinstance(version, str)
        assert version.strip()


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_import_no_exception():
    """Import should not raise unexpected exceptions."""
    try:
        import darkelf_shadow  # noqa: F401
    except Exception as exc:
        pytest.fail(f"Import failed: {exc}")


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_current_directory_exists():
    """Filesystem sanity check."""
    assert Path(".").exists()
