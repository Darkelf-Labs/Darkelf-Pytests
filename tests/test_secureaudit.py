"""
tests/test_secureaudit.py

Unit tests for Darkelf SecureAudit.
"""

from pathlib import Path

import pytest

scan_project = pytest.importorskip(
    "darkelf_secureaudit.scanner",
    reason="Darkelf SecureAudit not installed",
).scan_project

pytestmark = pytest.mark.secureaudit


# ---------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------


def test_secureaudit_import():
    """Package imports successfully."""
    import darkelf_secureaudit  # noqa: F401


def test_scanner_import():
    """Scanner module imports."""
    from darkelf_secureaudit.scanner import scan_project  # noqa: F401


# ---------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------


def test_scan_current_directory():
    """Current directory scans without crashing."""
    from darkelf_secureaudit.scanner import scan_project

    results = scan_project(Path("."))

    assert isinstance(results, dict)
    assert "score" in results
    assert "files" in results
    assert "findings" in results


def test_score_is_integer():
    from darkelf_secureaudit.scanner import scan_project

    results = scan_project(Path("."))

    assert isinstance(results["score"], int)


def test_files_scanned_nonnegative():
    from darkelf_secureaudit.scanner import scan_project

    results = scan_project(Path("."))

    assert results["files"] >= 0


# ---------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------


def test_findings_have_expected_categories():
    from darkelf_secureaudit.scanner import scan_project

    findings = scan_project(Path("."))["findings"]

    for category in ("GOOD", "INFO", "MEDIUM", "HIGH"):
        assert category in findings


def test_high_findings_is_list():
    from darkelf_secureaudit.scanner import scan_project

    findings = scan_project(Path("."))["findings"]

    assert isinstance(findings["HIGH"], list)


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_scan_empty_directory(tmp_path):
    """Scanning an empty directory should not fail."""
    from darkelf_secureaudit.scanner import scan_project

    results = scan_project(tmp_path)

    assert results["files"] == 0
    assert results["score"] == 0


def test_scan_single_python_file(tmp_path):
    """Scanner should process a single Python file."""

    source = tmp_path / "sample.py"

    source.write_text(
        """
def hello():
    return "world"
""",
        encoding="utf-8",
    )

    from darkelf_secureaudit.scanner import scan_project

    results = scan_project(source)

    assert results["files"] == 1


def test_scan_never_returns_negative_score():
    from darkelf_secureaudit.scanner import scan_project

    results = scan_project(Path("."))

    assert results["score"] >= 0


def test_scan_score_not_above_100():
    from darkelf_secureaudit.scanner import scan_project

    results = scan_project(Path("."))

    assert results["score"] <= 100
