"""
tests/test_dependency_guardian.py

Tests for Darkelf Dependency Guardian.
Designed to work both locally and in GitHub Actions.
"""

from __future__ import annotations

from importlib.util import find_spec

import pytest

pytestmark = pytest.mark.dependencyguardian

HAS_GUARDIAN = find_spec("guardian") is not None


# ---------------------------------------------------------------------
# Package Tests
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_import_package():
    """Package imports successfully."""
    import guardian  # noqa: F401


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_import_scanner():
    """Scanner module imports successfully."""
    from guardian import scanner  # noqa: F401

    assert scanner is not None


# ---------------------------------------------------------------------
# Requirement Parsing
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_parse_valid_requirement():
    """Parse a pinned requirement."""
    from guardian.scanner import parse_requirement

    pkg = parse_requirement("requests==2.32.0")

    assert pkg.name == "requests"
    assert pkg.version == "2.32.0"


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_parse_requirement_without_version():
    """Parse an unpinned requirement."""
    from guardian.scanner import parse_requirement

    pkg = parse_requirement("pytest")

    assert pkg.name == "pytest"


# ---------------------------------------------------------------------
# Requirements Files
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_read_requirements_file(tmp_path):
    """Read a requirements.txt file."""
    req = tmp_path / "requirements.txt"

    req.write_text(
        "requests==2.32.0\nurllib3==2.2.2\n",
        encoding="utf-8",
    )

    from guardian.scanner import load_requirements

    packages = load_requirements(req)

    assert len(packages) == 2


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_empty_requirements(tmp_path):
    """Empty requirements file returns an empty list."""
    req = tmp_path / "requirements.txt"
    req.write_text("", encoding="utf-8")

    from guardian.scanner import load_requirements

    assert load_requirements(req) == []


# ---------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_scan_requirements(tmp_path):
    """Single requirements file scan."""
    req = tmp_path / "requirements.txt"
    req.write_text("requests==2.32.0\n", encoding="utf-8")

    from guardian.scanner import scan_file

    results = scan_file(req)

    assert isinstance(results, dict)


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_scan_directory(tmp_path):
    """Project scan returns a dictionary."""
    req = tmp_path / "requirements.txt"
    req.write_text("pytest==8.4.1\n", encoding="utf-8")

    from guardian.scanner import scan_project

    results = scan_project(tmp_path)

    assert isinstance(results, dict)


# ---------------------------------------------------------------------
# Result Structure
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_results_have_keys(tmp_path):
    """Returned scan contains expected keys."""
    req = tmp_path / "requirements.txt"
    req.write_text("pytest==8.4.1\n", encoding="utf-8")

    from guardian.scanner import scan_project

    results = scan_project(tmp_path)

    assert isinstance(results, dict)
    assert "summary" in results
    assert "packages" in results


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_missing_file(tmp_path):
    """Missing files should raise FileNotFoundError."""
    from guardian.scanner import scan_file

    with pytest.raises(FileNotFoundError):
        scan_file(tmp_path / "missing.txt")


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_scan_empty_directory(tmp_path):
    """Scanning an empty directory should not crash."""
    from guardian.scanner import scan_project

    results = scan_project(tmp_path)

    assert isinstance(results, dict)


@pytest.mark.skipif(
    not HAS_GUARDIAN,
    reason="Dependency Guardian package/repository not available",
)
def test_scan_does_not_crash(tmp_path):
    """Malformed requirements should not crash the scanner."""
    req = tmp_path / "requirements.txt"

    req.write_text(
        "invalid=====\n",
        encoding="utf-8",
    )

    from guardian.scanner import scan_project

    scan_project(tmp_path)
