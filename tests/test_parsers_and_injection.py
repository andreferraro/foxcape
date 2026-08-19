from bs4 import BeautifulSoup

from foxcape.hardware_spoofing import (
    async_inject_hardware_and_webrtc_spoofing,
    get_deep_hardware_and_webrtc_spoof_script,
    inject_hardware_and_webrtc_spoofing,
)
from foxcape.noise_injector import (
    async_inject_fingerprint_noise,
    get_canvas_and_audio_noise_script,
    inject_fingerprint_noise,
)
from foxcape.parsers import build_soup, dom_to_markdown_summary, extract_clean_text, extract_links_from_soup


class ScriptPage:
    def __init__(self) -> None:
        self.scripts: list[str] = []

    def add_init_script(self, script: str) -> None:
        self.scripts.append(script)


class AsyncScriptPage:
    def __init__(self) -> None:
        self.scripts: list[str] = []

    async def add_init_script(self, script: str) -> None:
        self.scripts.append(script)


def test_build_soup_falls_back_for_invalid_parser() -> None:
    soup = build_soup("<html><title>x</title></html>", "not-a-parser")
    assert soup.find("title").get_text() == "x"


def test_text_link_and_markdown_helpers() -> None:
    soup = BeautifulSoup(
        """
        <html>
          <header>skip</header><h1>Title</h1><p>Body</p><ul><li>One</li></ul>
          <script>bad()</script><a href="/docs">Docs</a><a href="mailto:x@y.test">Mail</a>
        </html>
        """,
        "html.parser",
    )

    assert "skip" not in extract_clean_text(soup)
    assert extract_links_from_soup(soup, "https://example.com") == [
        {"text": "Docs", "href": "https://example.com/docs"}
    ]
    assert dom_to_markdown_summary(soup).splitlines()[0] == "# Title"


def test_noise_script_and_sync_injection() -> None:
    script = get_canvas_and_audio_noise_script(seed=123)
    assert "const SEED = 123" in script
    assert "CanvasRenderingContext2D" in script

    page = ScriptPage()
    inject_fingerprint_noise(page, seed=123)  # type: ignore[arg-type]
    assert page.scripts == [script]


async def test_async_noise_injection() -> None:
    page = AsyncScriptPage()
    await async_inject_fingerprint_noise(page, seed=456)  # type: ignore[arg-type]
    assert "const SEED = 456" in page.scripts[0]


def test_hardware_script_and_sync_injection() -> None:
    script = get_deep_hardware_and_webrtc_spoof_script()
    assert "hardwareConcurrency" in script
    assert "enumerateDevices" in script

    page = ScriptPage()
    inject_hardware_and_webrtc_spoofing(page)  # type: ignore[arg-type]
    assert page.scripts == [script]


async def test_async_hardware_injection() -> None:
    page = AsyncScriptPage()
    await async_inject_hardware_and_webrtc_spoofing(page)  # type: ignore[arg-type]
    assert "pdfViewerEnabled" in page.scripts[0]
