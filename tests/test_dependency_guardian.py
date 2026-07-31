"""
tests/test_dependency_guardian.py

Tests for Darkelf Dependency Guardian.
"""

from __future__ import annotations

import json
from importlib.util import find_spec

import pytest

pytestmark = pytest.mark.dependencyguardian

HAS_CORE = find_spec("core") is not None


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_import_scanner():
    from core.scanner import ProjectScanner

    assert ProjectScanner is not None


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_import_projectinfo():
    from core.scanner import ProjectInfo

    assert ProjectInfo is not None


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_create_scanner(tmp_path):
    from core.scanner import ProjectScanner

    scanner = ProjectScanner(tmp_path)

    assert scanner is not None


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_detect_npm(tmp_path):
    from core.scanner import ProjectScanner

    package = {
        "name": "demo",
        "version": "1.0.0",
        "dependencies": {
            "react": "^19.0.0",
        },
    }

    (tmp_path / "package.json").write_text(
        json.dumps(package),
        encoding="utf-8",
    )

    scanner = ProjectScanner(tmp_path)
    info = scanner.scan()

    assert info.package_manager == "npm"


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_detect_framework(tmp_path):
    from core.scanner import ProjectScanner

    package = {
        "name": "demo",
        "version": "1.0.0",
        "dependencies": {
            "next": "16.0.0",
        },
    }

    (tmp_path / "package.json").write_text(
        json.dumps(package),
        encoding="utf-8",
    )

    scanner = ProjectScanner(tmp_path)
    info = scanner.scan()

    assert info.framework == "Next.js"


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_scan_returns_projectinfo(tmp_path):
    from core.scanner import ProjectInfo, ProjectScanner

    (tmp_path / "package.json").write_text(
        '{"name":"demo"}',
        encoding="utf-8",
    )

    scanner = ProjectScanner(tmp_path)
    info = scanner.scan()

    assert isinstance(info, ProjectInfo)


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_dependencies_loaded(tmp_path):
    from core.scanner import ProjectScanner

    package = {
        "dependencies": {
            "react": "^19.0.0",
            "next": "^16.0.0",
        }
    }

    (tmp_path / "package.json").write_text(
        json.dumps(package),
        encoding="utf-8",
    )

    scanner = ProjectScanner(tmp_path)
    info = scanner.scan()

    assert "react" in info.all_packages
    assert "next" in info.all_packages


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_missing_package_json(tmp_path):
    from core.scanner import ProjectScanner

    scanner = ProjectScanner(tmp_path)

    with pytest.raises(FileNotFoundError):
        scanner.scan()


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_empty_package_json(tmp_path):
    from core.scanner import ProjectScanner

    (tmp_path / "package.json").write_text(
        "{}",
        encoding="utf-8",
    )

    scanner = ProjectScanner(tmp_path)

    info = scanner.scan()

    assert info is not None


@pytest.mark.skipif(
    not HAS_CORE,
    reason="Dependency Guardian package/repository not available",
)
def test_scan_does_not_crash(tmp_path):
    from core.scanner import ProjectScanner

    (tmp_path / "package.json").write_text(
        '{"dependencies":{"bad":"*"}}',
        encoding="utf-8",
    )

    scanner = ProjectScanner(tmp_path)

    scanner.scan()
