import hashlib
from unittest.mock import MagicMock, patch

from importlib.util import find_spec

import pytest

if find_spec("darkelf_cli") is None:
    pytest.skip(
        "Darkelf CLI Browser not installed",
        allow_module_level=True,
    )

from darkelf_cli import cli


# ----------------------------------------------------------
# Basic Constants
# ----------------------------------------------------------

def test_duck_url_exists():
    assert cli.DUCKDUCKGO_LITE.startswith("https://")


def test_user_agents_present():
    assert len(cli.USER_AGENTS) >= 3


def test_languages_present():
    assert len(cli.ACCEPT_LANGUAGES) >= 1


# ----------------------------------------------------------
# Headers
# ----------------------------------------------------------

def test_random_headers_returns_required_fields():
    headers = cli.random_headers()

    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "DNT" in headers


def test_random_headers_minimal():
    headers = cli.random_headers(
        {
            "minimal_headers": True,
        }
    )

    assert "Accept-Language" not in headers


def test_random_headers_noise():
    headers = cli.random_headers(
        {
            "add_noise_headers": True,
        }
    )

    assert "X-Request-ID" in headers


# ----------------------------------------------------------
# Logging
# ----------------------------------------------------------

def test_setup_logging():
    cli.setup_logging(debug=False)
    cli.setup_logging(debug=True)


# ----------------------------------------------------------
# Entropy
# ----------------------------------------------------------

def test_entropy():
    cli.ensure_strong_entropy(32)


# ----------------------------------------------------------
# Tracker Hash
# ----------------------------------------------------------

def test_tracker_hash():
    h = hashlib.sha256("google-analytics.com".encode()).hexdigest()

    assert h in cli.KNOWN_TRACKER_HASHES


# ----------------------------------------------------------
# DDG Parser
# ----------------------------------------------------------

def test_parse_ddg_empty():
    from bs4 import BeautifulSoup

    soup = BeautifulSoup("<html></html>", "html.parser")

    result = cli.parse_ddg_lite_results(soup)

    assert result == "no_results"


def test_parse_ddg_link():
    from bs4 import BeautifulSoup

    html = """
    <a href="https://example.com">
        Example
    </a>
    """

    soup = BeautifulSoup(html, "html.parser")

    results = cli.parse_ddg_lite_results(soup)

    assert len(results) == 1
    assert results[0][0] == "Example"


# ----------------------------------------------------------
# Network
# ----------------------------------------------------------

@patch("darkelf_cli.cli.requests.Session")
def test_fetch_requests(mock_session):
    response = MagicMock()
    response.text = "<html></html>"
    response.status_code = 200
    response.raise_for_status.return_value = None

    session = MagicMock()
    session.get.return_value = response

    mock_session.return_value = session

    html, headers = cli.fetch_with_requests(
        "https://example.com",
        debug=False,
    )

    assert "<html>" in html
    assert isinstance(headers, dict)


@patch("darkelf_cli.cli.requests.Session")
def test_fetch_isolated(mock_session):
    response = MagicMock()
    response.text = "<html></html>"
    response.headers = {}
    response.raise_for_status.return_value = None

    session = MagicMock()
    session.get.return_value = response

    mock_session.return_value = session

    html, hdrs = cli.fetch_with_isolated_session(
        "https://example.com"
    )

    assert "<html>" in html


# ----------------------------------------------------------
# Browser Object
# ----------------------------------------------------------

def test_browser_creation():
    browser = cli.DarkelfCLIBrowser()

    assert browser.page_size == 15
    assert browser.tabs == []


def test_set_theme():
    browser = cli.DarkelfCLIBrowser()

    browser.set_theme("dark")

    assert browser.theme_name == "dark"


def test_secure_wipe():
    browser = cli.DarkelfCLIBrowser()

    browser.history.append("https://example.com")
    browser.tabs.append(object())

    browser.secure_wipe()

    assert browser.history == []
    assert browser.tabs == []


# ----------------------------------------------------------
# Main Entry
# ----------------------------------------------------------

@patch("darkelf_cli.cli.main_menu")
def test_main_menu_called(mock_menu):
    with patch("sys.argv", ["darkelf-cli"]):
        cli.main()

    mock_menu.assert_called_once()


@patch("darkelf_cli.cli.run_browser_mode")
def test_browser_flag(mock_browser):
    with patch("sys.argv", ["darkelf-cli", "--browser"]):
        cli.main()

    mock_browser.assert_called_once()
