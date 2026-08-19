"""Shared fixtures for Foxcape tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from foxcape import FoxcapeConfig

SAMPLE_HTML = """<!DOCTYPE html><html><head><title>Test Page</title></head>
<body><header><nav><a href="/home">Home</a></nav></header>
<main><h1>Main Heading</h1><p>Paragraph<script>console.log("x");</script></p></main>
</body></html>"""


@pytest.fixture
def default_config() -> FoxcapeConfig:
    return FoxcapeConfig(
        headless=True,
        humanize=False,
        simulate_mouse=False,
        human_delay_range=None,
        use_markov_cadence=False,
        canvas_noise=False,
        audio_noise=False,
        hardware_spoofing=False,
    )


@pytest.fixture
def sample_html() -> str:
    return SAMPLE_HTML


def _build_mock_page(*, html: str = SAMPLE_HTML, url: str = "https://example.com") -> MagicMock:
    page = MagicMock()
    page.goto = MagicMock(return_value=MagicMock(status=200))
    page.content.return_value = html
    page.url = url
    page.close = MagicMock()
    page.wait_for_selector = MagicMock()
    return page


@pytest.fixture
def mock_camoufox(monkeypatch: pytest.MonkeyPatch) -> tuple[MagicMock, MagicMock]:
    """Patch sync Camoufox with a fake browser context."""
    page = _build_mock_page()
    browser = MagicMock()
    browser.pages = [page]
    browser.new_page = MagicMock(return_value=page)

    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=browser)
    cm.__exit__ = MagicMock(return_value=False)

    mock_cls = MagicMock(return_value=cm)
    monkeypatch.setattr("foxcape.scraper.Camoufox", mock_cls)
    return page, cm


@pytest.fixture
def mock_async_camoufox(monkeypatch: pytest.MonkeyPatch) -> tuple[MagicMock, MagicMock]:
    """Patch async AsyncCamoufox with a fake browser context."""
    page = _build_mock_page()
    page.goto = AsyncMock(return_value=MagicMock(status=200))
    page.content = AsyncMock(return_value=SAMPLE_HTML)
    page.close = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.add_init_script = AsyncMock()

    browser = MagicMock()
    browser.pages = [page]
    browser.new_page = AsyncMock(return_value=page)

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=browser)
    cm.__aexit__ = AsyncMock(return_value=False)

    mock_cls = MagicMock(return_value=cm)
    monkeypatch.setattr("foxcape.async_scraper.AsyncCamoufox", mock_cls)
    return page, cm
