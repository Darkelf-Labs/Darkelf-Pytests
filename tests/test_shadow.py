"""
tests/test_shadow.py

Tests for Darkelf Shadow.
Designed to work locally and in GitHub Actions without
launching the GUI.
"""

from __future__ import annotations

import platform
import sys
from importlib.util import find_spec
from pathlib import Path

import pytest

pytestmark = pytest.mark.shadow

HAS_SHADOW = find_spec("shadow") is not None


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------


def test_python_version():
    assert sys.version_info >= (3, 11)


def test_platform_supported():
    assert platform.system() in {"Darwin", "Linux", "Windows"}


def test_pyside6_available():
    try:
        import PySide6  # noqa: F401
    except ImportError:
        pytest.skip("PySide6 not installed")


def test_qtwebengine_available():
    try:
        from PySide6.QtWebEngineCore import QWebEngineProfile  # noqa: F401
    except ImportError:
        pytest.skip("QtWebEngine not available")


# ---------------------------------------------------------------------
# Package
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_package_import():
    import shadow  # noqa: F401


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_package_path_exists():
    import shadow

    assert Path(shadow.__file__).exists()


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_package_has_version():
    import shadow

    version = getattr(shadow, "__version__", None)

    if version is not None:
        assert isinstance(version, str)
        assert version.strip()


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_import_no_exception():
    try:
        import shadow  # noqa: F401
    except Exception as exc:
        pytest.fail(f"Import failed: {exc}")


# ---------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------


def test_current_directory_exists():
    assert Path(".").exists()
