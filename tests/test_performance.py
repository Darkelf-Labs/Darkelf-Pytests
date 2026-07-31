"""
tests/test_performance.py

Performance regression tests for the Darkelf Labs ecosystem.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.performance,
    pytest.mark.regression,
]


# ---------------------------------------------------------------------
# Repository root
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def repo_root():
    """Return the repository root."""
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------
# SecureAudit Performance
# ---------------------------------------------------------------------


def test_secureaudit_scan_completes(repo_root):
    """SecureAudit should finish within a reasonable time."""

    try:
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    start = time.perf_counter()
    results = scan_project(repo_root)
    elapsed = time.perf_counter() - start

    assert isinstance(results, dict)
    assert elapsed < 5.0


def test_secureaudit_repeatability(repo_root):
    """Repeated scans should complete successfully."""

    try:
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    durations = []

    for _ in range(3):
        start = time.perf_counter()
        scan_project(repo_root)
        durations.append(time.perf_counter() - start)

    assert max(durations) < 5.0


# ---------------------------------------------------------------------
# Dependency Guardian
# ---------------------------------------------------------------------


def test_dependency_guardian_scan_speed(repo_root):
    """Dependency Guardian should scan quickly."""

    try:
        from darkelf_dependency_guardian.scanner import scan_project
    except ImportError:
        pytest.skip("Dependency Guardian not installed")

    start = time.perf_counter()
    results = scan_project(repo_root)
    elapsed = time.perf_counter() - start

    assert isinstance(results, dict)
    assert elapsed < 5.0


# ---------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------


def test_directory_walk_speed(repo_root):
    """Walking the repository should be fast."""

    start = time.perf_counter()

    files = [
        p
        for p in repo_root.rglob("*")
        if ".git" not in p.parts
    ]

    elapsed = time.perf_counter() - start

    assert files
    assert elapsed < 2.0


# ---------------------------------------------------------------------
# Import Performance
# ---------------------------------------------------------------------


def test_import_time():
    """SecureAudit import should be reasonably quick."""

    try:
        start = time.perf_counter()

        import darkelf_secureaudit  # noqa: F401

        elapsed = time.perf_counter() - start

    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    assert elapsed < 2.0


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_perf_counter_monotonic():
    first = time.perf_counter()
    second = time.perf_counter()

    assert second >= first


def test_time_module_available():
    assert isinstance(time.perf_counter(), float)


def test_repository_not_empty(repo_root):
    """Repository should contain files."""

    assert any(repo_root.iterdir())


def test_multiple_scans_consistent(repo_root):
    """Scanning should always return the same score."""

    try:
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    scores = []

    for _ in range(3):
        scores.append(scan_project(repo_root)["score"])

    assert len(set(scores)) == 1
