"""
tests/test_utils.py

Generic utility tests for the Darkelf Labs ecosystem.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

pytestmark = pytest.mark.regression


# ---------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------


def test_sha256_length():
    """SHA-256 digests should be 64 hex characters."""
    digest = hashlib.sha256(b"Darkelf").hexdigest()

    assert len(digest) == 64


def test_sha256_repeatable():
    """Hashing the same data should produce the same digest."""
    a = hashlib.sha256(b"Darkelf").hexdigest()
    b = hashlib.sha256(b"Darkelf").hexdigest()

    assert a == b


def test_sha256_different_inputs():
    """Different inputs should produce different hashes."""
    a = hashlib.sha256(b"Darkelf").hexdigest()
    b = hashlib.sha256(b"Shadow").hexdigest()

    assert a != b


# ---------------------------------------------------------------------
# Path Utilities
# ---------------------------------------------------------------------


def test_current_directory():
    """Current directory should exist."""
    assert Path(".").exists()


def test_parent_directory():
    """Parent directory should exist."""
    assert Path(".").parent.exists()


def test_resolve_absolute():
    """Resolved paths should be absolute."""
    assert Path(".").resolve().is_absolute()


# ---------------------------------------------------------------------
# String Helpers
# ---------------------------------------------------------------------


def test_strip_whitespace():
    assert "  Darkelf  ".strip() == "Darkelf"


def test_lowercase():
    assert "DarkELF".lower() == "darkelf"


def test_uppercase():
    assert "Darkelf".upper() == "DARKELF"


def test_split():
    value = "one,two,three".split(",")

    assert value == ["one", "two", "three"]


# ---------------------------------------------------------------------
# Lists
# ---------------------------------------------------------------------


def test_list_sort():
    values = [4, 2, 1, 3]

    values.sort()

    assert values == [1, 2, 3, 4]


def test_unique_values():
    values = {1, 2, 3}

    assert values == {1, 2, 3}


# ---------------------------------------------------------------------
# Dictionaries
# ---------------------------------------------------------------------


def test_dictionary_lookup():
    data = {
        "browser": "Shadow",
        "version": "7.0.4",
    }

    assert data["browser"] == "Shadow"


def test_dictionary_get():
    data = {}

    assert data.get("missing") is None


# ---------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------


def test_integer_math():
    assert 2 + 2 == 4


def test_float_round():
    assert round(3.14159, 2) == 3.14


# ---------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------


def test_path_join():
    path = Path("tests") / "data"

    assert path.parts[-1] == "data"


def test_file_suffix():
    path = Path("sample.py")

    assert path.suffix == ".py"


# ---------------------------------------------------------------------
# Regression
# ---------------------------------------------------------------------


def test_boolean_truth():
    assert True


def test_boolean_false():
    assert not False


def test_none_value():
    value = None

    assert value is None
