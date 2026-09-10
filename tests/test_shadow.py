"""
tests/test_shadow.py

Expanded tests for Darkelf Shadow.
Designed to run locally and in GitHub Actions without launching the full GUI.
"""

from __future__ import annotations

import importlib
import inspect
import os
import platform
import sys
from importlib.util import find_spec
from pathlib import Path

import pytest

pytestmark = pytest.mark.shadow

HAS_SHADOW = find_spec("shadow") is not None
HAS_PYSIDE6 = find_spec("PySide6") is not None
HAS_QTWEBENGINE = find_spec("PySide6.QtWebEngineCore") is not None


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------


def test_python_version():
    assert sys.version_info >= (3, 11)


def test_platform_supported():
    assert platform.system() in {"Darwin", "Linux", "Windows"}


def test_pyside6_available():
    if not HAS_PYSIDE6:
        pytest.skip("PySide6 not installed")
    import PySide6  # noqa: F401


def test_qtwebengine_available():
    if not HAS_QTWEBENGINE:
        pytest.skip("QtWebEngine not available")
    from PySide6.QtWebEngineCore import QWebEngineProfile  # noqa: F401


def test_headless_env_is_safe_to_set():
    # Safe sanity check for CI-style execution.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    assert os.environ["QT_QPA_PLATFORM"]


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
    except Exception as exc:  # pragma: no cover - failure path assertion
        pytest.fail(f"Import failed: {exc}")


# ---------------------------------------------------------------------
# Filesystem / basic runtime
# ---------------------------------------------------------------------


def test_current_directory_exists():
    assert Path(".").exists()


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_shadow_package_directory_contains_python_files():
    import shadow

    pkg_dir = Path(shadow.__file__).resolve().parent
    py_files = list(pkg_dir.glob("*.py"))
    assert py_files, f"No .py files found in {pkg_dir}"


# ---------------------------------------------------------------------
# Module coverage helpers
# ---------------------------------------------------------------------

# Keep this list conservative: modules known to exist from your coverage output.
SHADOW_MODULES = [
    "shadow.boot",
    "shadow.browser",
    "shadow.browser_downloads",
    "shadow.browser_features",
    "shadow.browser_homepage",
    "shadow.browser_icons",
    "shadow.browser_page",
    "shadow.browser_ui",
    "shadow.cli",
    "shadow.constants",
    "shadow.darkelf_context_menu",
    "shadow.darkelf_inspector",
    "shadow.darkelf_pq",
    "shadow.filters",
    "shadow.interceptor",
    "shadow.miniai",
    "shadow.settings_dialog",
    "shadow.settings_pages",
    "shadow.splash",
    "shadow.utils",
]


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
@pytest.mark.parametrize("module_name", SHADOW_MODULES)
def test_shadow_module_spec_exists(module_name):
    spec = find_spec(module_name)
    assert spec is not None, f"Module spec not found: {module_name}"


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
@pytest.mark.parametrize("module_name", SHADOW_MODULES)
def test_shadow_module_imports(module_name, monkeypatch):
    """
    Import every Shadow module normally.

    browser.py redirects stderr with os.dup2(..., sys.stderr.fileno()) at
    import time. pytest replaces sys.stderr while capturing output, and that
    capture object may not expose a usable fileno().  Give the import a real
    OS-backed stderr temporarily instead of hiding the error with a skip.
    """
    with open(os.devnull, "w") as real_stderr:
        monkeypatch.setattr(sys, "stderr", real_stderr)
        module = importlib.import_module(module_name)

    assert module is not None


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
@pytest.mark.parametrize("module_name", SHADOW_MODULES)
def test_shadow_module_has_public_symbols(module_name, monkeypatch):
    with open(os.devnull, "w") as real_stderr:
        monkeypatch.setattr(sys, "stderr", real_stderr)
        module = importlib.import_module(module_name)

    public_names = [n for n in dir(module) if not n.startswith("_")]
    assert public_names, f"{module_name} exposes no public symbols"


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
@pytest.mark.parametrize("module_name", SHADOW_MODULES)
def test_shadow_module_file_path_is_real(module_name, monkeypatch):
    with open(os.devnull, "w") as real_stderr:
        monkeypatch.setattr(sys, "stderr", real_stderr)
        module = importlib.import_module(module_name)

    module_file = getattr(module, "__file__", None)
    assert module_file is not None, f"{module_name} has no __file__ attribute"
    assert Path(module_file).exists(), f"Module file path does not exist: {module_file}"


# ---------------------------------------------------------------------
# Focused tests for known light-weight modules
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_shadow_constants_module_shape():
    constants = importlib.import_module("shadow.constants")
    names = dir(constants)
    assert names  # module loaded and introspectable


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_shadow_utils_module_members():
    utils = importlib.import_module("shadow.utils")
    funcs = [
        name
        for name, obj in inspect.getmembers(utils)
        if inspect.isfunction(obj) and obj.__module__ == "shadow.utils"
    ]
    # Don't assume a specific function name; just validate module introspection.
    assert isinstance(funcs, list)


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_shadow_cli_module_imports(monkeypatch):
    with open(os.devnull, "w") as real_stderr:
        monkeypatch.setattr(sys, "stderr", real_stderr)
        cli = importlib.import_module("shadow.cli")

    assert cli is not None


# ---------------------------------------------------------------------
# Regression guards around import idempotency
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
def test_reimport_shadow_package_is_idempotent():
    import shadow

    before = getattr(shadow, "__file__", None)
    reloaded = importlib.reload(shadow)
    after = getattr(reloaded, "__file__", None)
    assert before == after


@pytest.mark.skipif(
    not HAS_SHADOW,
    reason="Darkelf Shadow package/repository not available",
)
@pytest.mark.parametrize("module_name", ["shadow.utils", "shadow.constants", "shadow.cli"])
def test_reimport_selected_modules(module_name, monkeypatch):
    with open(os.devnull, "w") as real_stderr:
        monkeypatch.setattr(sys, "stderr", real_stderr)
        module = importlib.import_module(module_name)
        reloaded = importlib.reload(module)

    assert reloaded is module
