"""
tests/test_cocoa.py

Tests for Darkelf Cocoa.
Designed to work both locally and in GitHub Actions.
"""

from __future__ import annotations

import platform
import sys
from importlib.util import find_spec
from pathlib import Path

import pytest

pytestmark = pytest.mark.cocoa

HAS_COCOA = find_spec("darkelf_cocoa") is not None


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------


def test_python_version():
    """Darkelf Cocoa requires Python 3.11+."""
    assert sys.version_info >= (3, 11)


def test_running_on_macos():
    """Darkelf Cocoa is macOS-only."""
    if platform.system() != "Darwin":
        pytest.skip("Darkelf Cocoa is macOS-only")


def test_pyobjc_installed():
    """PyObjC should be importable."""
    if platform.system() != "Darwin":
        pytest.skip("Darkelf Cocoa is macOS-only")

    pytest.importorskip(
        "AppKit",
        reason="PyObjC (AppKit) not installed",
    )
    pytest.importorskip(
        "Foundation",
        reason="PyObjC (Foundation) not installed",
    )


def test_webkit_available():
    """WebKit framework should be importable."""
    if platform.system() != "Darwin":
        pytest.skip("Darkelf Cocoa is macOS-only")

    pytest.importorskip(
        "WebKit",
        reason="PyObjC WebKit bindings not installed",
    )


# ---------------------------------------------------------------------
# Package Tests
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_COCOA,
    reason="Darkelf Cocoa package/repository not available",
)
def test_package_import():
    """Package imports successfully."""
    import darkelf_cocoa  # noqa: F401


@pytest.mark.skipif(
    not HAS_COCOA,
    reason="Darkelf Cocoa package/repository not available",
)
def test_main_module_import():
    """Browser module imports."""
    from darkelf_cocoa import browser  # noqa: F401


@pytest.mark.skipif(
    not HAS_COCOA,
    reason="Darkelf Cocoa package/repository not available",
)
def test_package_location():
    """Installed package has a valid location."""
    import darkelf_cocoa

    assert Path(darkelf_cocoa.__file__).exists()


@pytest.mark.skipif(
    not HAS_COCOA,
    reason="Darkelf Cocoa package/repository not available",
)
def test_version_string():
    """Version should be a non-empty string if exported."""
    import darkelf_cocoa

    version = getattr(darkelf_cocoa, "__version__", None)

    if version is not None:
        assert isinstance(version, str)
        assert version.strip()


@pytest.mark.skipif(
    not HAS_COCOA,
    reason="Darkelf Cocoa package/repository not available",
)
def test_browser_module_exists():
    """Browser module loads."""
    from darkelf_cocoa import browser

    assert browser is not None


@pytest.mark.skipif(
    not HAS_COCOA,
    reason="Darkelf Cocoa package/repository not available",
)
def test_import_without_exception():
    """Import should never unexpectedly fail."""
    try:
        import darkelf_cocoa  # noqa: F401
    except Exception as exc:
        pytest.fail(f"Import raised exception: {exc}")


# ---------------------------------------------------------------------
# General Regression
# ---------------------------------------------------------------------


def test_current_directory_exists():
    """Filesystem sanity check."""
    assert Path(".").exists()


def test_platform_value():
    """Platform name should always be available."""
    assert isinstance(platform.system(), str)
    assert platform.system()
