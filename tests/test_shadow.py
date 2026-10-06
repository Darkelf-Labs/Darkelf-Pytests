"""Shadow behavior regressions plus module-import smoke tests.

Uses tiny in-memory filter lists and a loopback HTTP server. No subscription
updates or public website requests are made. The large View Source test uses
a real Qt renderer in a separate process, without starting the full browser.
Set DARKELF_TEST_WEBENGINE=0 only to explicitly skip that renderer test.
"""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.util import find_spec
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import pytest

pytestmark = pytest.mark.shadow


def _available(name):
    try:
        return find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


HAS_SHADOW = _available("shadow")
SHADOW_MODULES = (
    "boot", "browser", "browser_downloads", "browser_features",
    "browser_homepage", "browser_icons", "browser_page", "browser_ui",
    "cli", "constants", "darkelf_context_menu", "darkelf_inspector",
    "darkelf_pq", "filters", "interceptor", "miniai", "settings_dialog",
    "settings_pages", "splash", "utils",
)


@pytest.fixture
def shadow_module(monkeypatch, tmp_path):
    if not HAS_SHADOW:
        pytest.skip("Install/check out Darkelf Shadow to run Shadow tests")
    original_expanduser = os.path.expanduser
    monkeypatch.setattr(
        os.path, "expanduser",
        lambda value: str(tmp_path) if value == "~" else original_expanduser(value),
    )

    def load(name):
        # Keep compatibility with source versions that access stderr.fileno().
        with open(os.devnull, "w") as real_stderr, monkeypatch.context() as context:
            context.setattr(sys, "stderr", real_stderr)
            module = importlib.import_module(f"shadow.{name}")
        return module

    return load


@pytest.mark.parametrize("name", SHADOW_MODULES)
def test_shadow_modules_import(name, shadow_module):
    module = shadow_module(name)
    assert Path(module.__file__).is_file()


def test_shadow_package_import():
    if not HAS_SHADOW:
        pytest.skip("Darkelf Shadow is not installed")
    import shadow

    assert Path(shadow.__file__).is_file()


@pytest.mark.parametrize(
    "url,expected_host",
    [
        ("https://www.youtube.com/watch?v=example&hl=vi&gl=VN", "www.youtube.com"),
        ("https://music.youtube.com/watch?v=example", "music.youtube.com"),
    ],
)
def test_youtube_locale_preserves_video(url, expected_host, shadow_module):
    result = urlparse(shadow_module("browser").force_youtube_locale(url))
    query = parse_qs(result.query)
    assert result.hostname == expected_host
    assert query["v"] == ["example"]
    assert query["hl"] == ["en"]
    assert query["gl"] == ["US"]


def test_youtube_locale_does_not_rewrite_lookalike_host(shadow_module):
    url = "https://youtube.com.example.net/watch?v=example&gl=VN"
    assert shadow_module("browser").force_youtube_locale(url) == url


@pytest.fixture
def filter_engine(shadow_module):
    filters = shadow_module("filters")

    def build(text):
        engine = filters.EasyListEngine()
        engine._parse_texts([text])
        engine._finalize()
        return engine

    return build


@pytest.mark.parametrize(
    "rule,url,resource,expected",
    [
        ("||ads.example.net^", "https://ads.example.net/a.js", "script", True),
        ("||ads.example.net^", "https://sub.ads.example.net/a.js", "script", True),
        ("||ads.example.net^", "https://notads.example.net/a.js", "script", False),
        ("||ads.example.net^", "https://ads.example.net.evil.net/a.js", "script", False),
        ("||ads.example.net^$image", "https://ads.example.net/pixel", "image", True),
        ("||ads.example.net^$image", "https://ads.example.net/a.js", "script", False),
        ("||ads.example.net^", "https://ads.example.net/", "document", False),
        ("/banner*ad.js", "https://cdn.example.net/banner-video-ad.js", "script", True),
    ],
)
def test_filter_matching_boundaries(rule, url, resource, expected, filter_engine):
    engine = filter_engine(rule)
    assert engine.should_block(url, "https://news.example.com/", resource) is expected


def test_filter_exception_overrides_normal_rule(filter_engine):
    engine = filter_engine(
        "||ads.example.net^\n@@||ads.example.net^$image"
    )
    url = "https://ads.example.net/resource"
    assert engine.should_block(url, "https://news.example.com/", "image") is False
    assert engine.should_block(url, "https://news.example.com/", "script") is True


def test_filter_domain_option_limits_first_party(filter_engine):
    engine = filter_engine("||ads.example.net^$domain=example.com")
    url = "https://ads.example.net/a.js"
    assert engine.should_block(url, "https://news.example.com/", "script") is True
    assert engine.should_block(url, "https://news.other.com/", "script") is False


def test_filter_same_site_core_resources_remain_allowed(filter_engine):
    engine = filter_engine("||cdn.example.com^")
    assert engine.should_block(
        "https://cdn.example.com/app.js", "https://news.example.com/", "script"
    ) is False


@pytest.mark.parametrize(
    "unsupported",
    [
        "||ads.example.net^$cookie",
        "ads.example.net#%#//scriptlet('example')",
        "ads.example.net#$#body { display: none; }",
        "ads.example.net#?#.advert",
    ],
)
def test_unsupported_page_actions_do_not_become_network_blocks(unsupported, filter_engine):
    engine = filter_engine(unsupported)
    assert engine.network_rules == []
    assert engine.should_block(
        "https://ads.example.net/a.js", "https://news.example.com/", "script"
    ) is False


def test_cosmetic_rules_do_not_become_network_rules(filter_engine):
    engine = filter_engine("example.com##.advert")
    assert not engine.network_rules
    assert ".advert" in engine.css_for_host("news.example.com")
    assert ".advert" not in engine.css_for_host("unrelated.net")


def test_filter_diagnostic_resets_after_allowed_request(filter_engine):
    engine = filter_engine("||ads.example.net^")
    assert engine.should_block(
        "https://ads.example.net/a.js", "https://news.example.com/", "script"
    ) is True
    assert engine.last_matched_rule
    assert engine.should_block(
        "https://cdn.other.net/app.js", "https://news.example.com/", "script"
    ) is False
    assert engine.last_matched_rule is None


def test_compiled_merge_deduplicates_and_applies_badfilter(shadow_module, filter_engine):
    filters = shadow_module("filters")
    merged = filters.EasyListEngine._compile_darkelf_filter([
        "||ads.example.net^\n||ads.example.net^\n||disabled.example.net^",
        "||disabled.example.net^$badfilter",
    ])
    engine = filter_engine(merged)
    assert [rule.raw for rule in engine.network_rules] == ["||ads.example.net^"]


def test_merge_cache_reused_and_corruption_rebuilt(shadow_module, monkeypatch, tmp_path):
    filters = shadow_module("filters")
    compiled_path = tmp_path / "compiled.txt"
    monkeypatch.setattr(filters, "EASYLIST_CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(filters, "DARKELF_COMPILED_FILTER", str(compiled_path))
    monkeypatch.setattr(
        filters.EasyListEngine, "fetch_lists", lambda self, urls: ["||ads.example.net^"]
    )
    original_merge = filters.EasyListEngine._compile_darkelf_filter
    calls = []

    def merge(texts):
        calls.append(1)
        return original_merge(texts)

    monkeypatch.setattr(filters.EasyListEngine, "_compile_darkelf_filter", staticmethod(merge))
    urls = ["https://lists.example.net/test.txt"]
    for _ in range(2):
        engine = filters.EasyListEngine()
        engine.load_and_build(urls)
        assert engine.should_block(
            "https://ads.example.net/a.js", "https://news.example.com/", "script"
        ) is True
    assert len(calls) == 1
    with compiled_path.open("a", encoding="utf-8") as stream:
        stream.write("\n||tampered.example.net^\n")
    engine = filters.EasyListEngine()
    engine.load_and_build(urls)
    assert len(calls) == 2
    assert not any("tampered.example.net" in rule.raw for rule in engine.network_rules)


@pytest.fixture
def source_server(tmp_path):
    raw_html = "<!doctype html><p>server HTML &amp; literal source</p>"
    secret = tmp_path / "private.txt"
    secret.write_text("DARKELF_SOURCE_TEST_PRIVATE", encoding="utf-8")
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            if self.path in ("/redirect", "/file-redirect", "/loop"):
                locations = {
                    "/redirect": "/raw",
                    "/file-redirect": secret.as_uri(),
                    "/loop": "/loop",
                }
                self.send_response(302)
                self.send_header("Location", locations[self.path])
                self.end_headers()
                return
            if self.path == "/error":
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            charset = "iso-8859-1" if self.path == "/charset" else "utf-8"
            self.send_header("Content-Type", f"text/html; charset={charset}")
            self.end_headers()
            body = "<p>caf\u00e9</p>" if self.path == "/charset" else raw_html
            self.wfile.write(body.encode(charset))

        def log_message(self, *_args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield SimpleNamespace(
            base=f"http://127.0.0.1:{server.server_port}",
            html=raw_html, secret=secret, requests=requests,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


@pytest.fixture
def open_source(shadow_module):
    browser = shadow_module("browser")

    def fetch(url):
        rendered = []
        receiver = SimpleNamespace(_show_source_tab=rendered.append)
        browser.DarkelfBrowser.open_source(receiver, url)
        assert len(rendered) == 1, "View Source must produce source or an error"
        return rendered[0]

    return fetch


@pytest.mark.parametrize("path", ["/raw", "/redirect"])
def test_view_source_fetches_server_html(path, source_server, open_source):
    assert open_source(source_server.base + path) == source_server.html


def test_view_source_respects_response_charset(source_server, open_source):
    assert open_source(source_server.base + "/charset") == "<p>caf\u00e9</p>"


@pytest.mark.parametrize("scheme", ["file", "ftp", "data"])
def test_view_source_rejects_non_web_schemes(scheme, source_server, open_source):
    urls = {
        "file": source_server.secret.as_uri(),
        "ftp": "ftp://127.0.0.1/private.txt",
        "data": "data:text/html,private",
    }
    text = open_source(urls[scheme])
    assert "Unable to load source" in text
    assert "DARKELF_SOURCE_TEST_PRIVATE" not in text
    assert not source_server.requests


def test_view_source_rejects_redirect_to_local_file(source_server, open_source):
    text = open_source(source_server.base + "/file-redirect")
    assert "Unable to load source" in text
    assert "DARKELF_SOURCE_TEST_PRIVATE" not in text


def test_view_source_bounds_redirect_loop(source_server, open_source):
    text = open_source(source_server.base + "/loop")
    assert "Unable to load source" in text
    assert len(source_server.requests) <= 10, "Redirect loop must stop promptly"


def test_view_source_reports_http_errors(source_server, open_source):
    assert "Unable to load source" in open_source(source_server.base + "/error")


def _render_source_probe():
    """Executed in a child process so renderer failures cannot crash pytest."""
    import tempfile
    from unittest.mock import patch

    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication, QTabWidget, QWidget

    app = QApplication.instance() or QApplication(["darkelf-source-test"])
    original_expanduser = os.path.expanduser
    with tempfile.TemporaryDirectory(prefix="darkelf-source-test-") as runtime_dir:
        with patch(
            "os.path.expanduser",
            side_effect=lambda value: runtime_dir if value == "~" else original_expanduser(value),
        ):
            browser = importlib.import_module("shadow.browser")

        class Harness(QWidget):
            def __init__(self):
                super().__init__()
                self.tabs = QTabWidget(self)

            def _exit_video_fullscreen(self):
                pass

        window = Harness()
        window.resize(800, 600)
        window.tabs.resize(800, 600)
        window.show()
        # Exceeds setHtml's data-URL limit and checks literal entity handling.
        html = (
            "<p>&amp; <script>window.DARKELF_TEST_EXECUTED=true</script>\u2603</p>"
            + "x<&>" * 650_000
        )
        browser.DarkelfBrowser._show_source_tab(window, html)
        deadline = time.monotonic() + 12
        matched = False
        while time.monotonic() < deadline:
            loop = QEventLoop()
            QTimer.singleShot(50, loop.quit)
            loop.exec()
            result = []
            loop = QEventLoop()

            def received(value, results=result, event_loop=loop):
                results.append(value)
                event_loop.quit()

            window.tabs.currentWidget().page().runJavaScript(
                "JSON.stringify({text:document.querySelector('pre')?.textContent,"
                "executed:window.DARKELF_TEST_EXECUTED===true})", received,
            )
            QTimer.singleShot(1000, loop.quit)
            loop.exec()
            value = json.loads(result[0]) if result and result[0] else {}
            if value.get("text") == html:
                assert value.get("executed") is False, "Source HTML must not execute"
                matched = True
                break
        from PySide6.QtCore import QCoreApplication, QEvent

        window.close()
        window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
        assert matched, "Large View Source was blank, truncated or not displayed as literal text"
        print("DARKELF_REAL_QT_SOURCE_PASS", flush=True)


def test_view_source_large_literal_html_in_real_qt(tmp_path):
    if not HAS_SHADOW:
        pytest.skip("Darkelf Shadow is not installed")
    if os.environ.get("DARKELF_TEST_WEBENGINE", "1") == "0":
        pytest.skip("Real renderer test explicitly disabled by DARKELF_TEST_WEBENGINE=0")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in sys.path if path)
    if sys.platform.startswith("linux") and not env.get("DISPLAY"):
        env.setdefault("QT_QPA_PLATFORM", "offscreen")
    if sys.platform.startswith("linux") and os.geteuid() == 0:
        # Confined to the isolated test renderer; never changes browser source.
        env["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    script = "import runpy,sys; runpy.run_path(sys.argv[1])['_render_source_probe']()"
    result = subprocess.run(
        [sys.executable, "-c", script, str(Path(__file__).resolve())],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=40, check=False,
    )
    diagnostic = (result.stdout + result.stderr)[-5000:]
    assert result.returncode == 0, diagnostic
    assert "DARKELF_REAL_QT_SOURCE_PASS" in result.stdout, diagnostic
