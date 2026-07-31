"""
tests/test_security.py

Common security regression tests.
"""

from __future__ import annotations

import os
import secrets
import tempfile
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.security,
    pytest.mark.regression,
]


# ---------------------------------------------------------------------
# Randomness
# ---------------------------------------------------------------------


def test_secrets_returns_string():
    """Ensure secrets.token_hex() returns a non-empty string."""
    token = secrets.token_hex(16)

    assert isinstance(token, str)
    assert len(token) == 32


def test_random_tokens_are_unique():
    """Generated tokens should not repeat."""
    token1 = secrets.token_hex(16)
    token2 = secrets.token_hex(16)

    assert token1 != token2


# ---------------------------------------------------------------------
# Temporary Files
# ---------------------------------------------------------------------


def test_temp_directory_exists():
    """System temporary directory should exist."""
    temp_dir = Path(tempfile.gettempdir())

    assert temp_dir.exists()
    assert temp_dir.is_dir()


def test_named_temp_file():
    """Temporary file should be writable."""
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        temp.write(b"Darkelf")
        temp.flush()

        assert Path(temp.name).exists()


# ---------------------------------------------------------------------
# Path Handling
# ---------------------------------------------------------------------


def test_path_resolution():
    """Resolved paths should be absolute."""
    path = Path(".").resolve()

    assert path.is_absolute()


def test_path_traversal_normalization():
    """
    Ensure '..' components are resolved.
    """
    normalized = Path("tests/../README.md").resolve()

    assert ".." not in str(normalized)


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------


def test_environment_is_dictionary():
    """Environment variables are available."""
    assert isinstance(os.environ, os._Environ)


def test_current_working_directory_exists():
    """Current working directory should exist."""
    cwd = Path.cwd()

    assert cwd.exists()
    assert cwd.is_dir()


# ---------------------------------------------------------------------
# File Permissions
# ---------------------------------------------------------------------


def test_can_create_temp_directory():
    """Creating a temporary directory should succeed."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)

        assert path.exists()
        assert path.is_dir()


# ---------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------


def test_utf8_roundtrip():
    """UTF-8 encoding/decoding should be lossless."""
    text = "Darkelf Security"

    encoded = text.encode("utf-8")
    decoded = encoded.decode("utf-8")

    assert decoded == text


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_no_null_bytes_in_paths():
    """Null bytes should not appear in filesystem paths."""
    assert "\x00" not in str(Path.cwd())


def test_safe_join():
    """Basic safe path join."""
    path = Path("tests") / "data"

    assert str(path).endswith("data")


def test_path_object_type():
    """Path objects should remain pathlib.Path instances."""
    assert isinstance(Path("."), Path)
