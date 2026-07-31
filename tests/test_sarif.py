"""
tests/test_sarif.py

Tests for SARIF report generation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.secureaudit,
    pytest.mark.integration,
]


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def sample_project():
    return Path(__file__).parent / "data" / "sample_project"


# ---------------------------------------------------------------------
# SARIF Generation
# ---------------------------------------------------------------------


def test_generate_sarif(sample_project, tmp_path):
    """Generate a SARIF report."""

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    results = scan_project(sample_project)

    outfile = tmp_path / "report.sarif"

    write_sarif(results, outfile)

    assert outfile.exists()


def test_sarif_is_valid_json(sample_project, tmp_path):
    """Generated SARIF should be valid JSON."""

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    outfile = tmp_path / "report.sarif"

    write_sarif(
        scan_project(sample_project),
        outfile,
    )

    with outfile.open(
        "r",
        encoding="utf-8",
    ) as fp:
        data = json.load(fp)

    assert isinstance(data, dict)


# ---------------------------------------------------------------------
# SARIF Schema
# ---------------------------------------------------------------------


def test_sarif_has_version(sample_project, tmp_path):

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    outfile = tmp_path / "report.sarif"

    write_sarif(
        scan_project(sample_project),
        outfile,
    )

    data = json.loads(outfile.read_text())

    assert "version" in data


def test_sarif_has_runs(sample_project, tmp_path):

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    outfile = tmp_path / "report.sarif"

    write_sarif(
        scan_project(sample_project),
        outfile,
    )

    data = json.loads(outfile.read_text())

    assert "runs" in data
    assert isinstance(data["runs"], list)


def test_sarif_contains_tool(sample_project, tmp_path):

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    outfile = tmp_path / "report.sarif"

    write_sarif(
        scan_project(sample_project),
        outfile,
    )

    data = json.loads(outfile.read_text())

    assert "tool" in data["runs"][0]


def test_sarif_contains_results(sample_project, tmp_path):

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    outfile = tmp_path / "report.sarif"

    write_sarif(
        scan_project(sample_project),
        outfile,
    )

    data = json.loads(outfile.read_text())

    assert "results" in data["runs"][0]


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_multiple_generations_identical(sample_project, tmp_path):

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    result = scan_project(sample_project)

    first = tmp_path / "first.sarif"
    second = tmp_path / "second.sarif"

    write_sarif(result, first)
    write_sarif(result, second)

    assert first.read_text() == second.read_text()


def test_sarif_file_not_empty(sample_project, tmp_path):

    try:
        from darkelf_secureaudit.sarif import write_sarif
        from darkelf_secureaudit.scanner import scan_project
    except ImportError:
        pytest.skip("Darkelf SecureAudit not installed")

    outfile = tmp_path / "report.sarif"

    write_sarif(
        scan_project(sample_project),
        outfile,
    )

    assert outfile.stat().st_size > 0
