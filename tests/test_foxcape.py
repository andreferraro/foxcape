"""Sync Foxcape lifecycle and scrape path (mocked Camoufox)."""

from unittest.mock import MagicMock, patch

import pytest

from foxcape import BrowserStartupError, Foxcape, FoxcapeConfig


def test_context_manager_lifecycle(mock_camoufox: tuple) -> None:
    page, cm = mock_camoufox
    with Foxcape(FoxcapeConfig(headless=True)) as fox:
        assert fox.browser is not None
        assert fox.page is page
    page.close.assert_called_once()
    cm.__exit__.assert_called_once()


def test_get_returns_foxcape_result(mock_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    page, _ = mock_camoufox
    fox = Foxcape(default_config)
    result = fox.get("https://example.com", human_delay=False, simulate_mouse=False)
    page.goto.assert_called_once()
    assert result.title == "Test Page"
    assert result.select_one("h1") is not None
    fox.close()


def test_fetch_classmethod(mock_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    result = Foxcape.fetch("https://example.com", config=default_config, human_delay=False)
    assert result.title == "Test Page"


def test_start_raises_browser_startup_error_when_camoufox_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_args, **_kwargs):
        raise RuntimeError("browser binary not found")

    monkeypatch.setattr("foxcape.scraper.Camoufox", boom)
    fox = Foxcape(FoxcapeConfig(headless=True))
    with pytest.raises(BrowserStartupError, match="camoufox fetch"):
        fox.start()


def test_start_is_idempotent(mock_camoufox: tuple) -> None:
    _, cm = mock_camoufox
    fox = Foxcape(FoxcapeConfig(headless=True))
    fox.start()
    fox.start()
    cm.__enter__.assert_called_once()


def test_evaluate_with_and_without_arg(mock_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    page, _ = mock_camoufox
    page.evaluate.return_value = 42
    fox = Foxcape(default_config)
    assert fox.evaluate("1+1") == 42
    assert fox.evaluate("fn", {"x": 1}) == 42
    page.evaluate.assert_any_call("1+1")
    page.evaluate.assert_any_call("fn", {"x": 1})
    fox.close()


def test_type_human_delegates_to_human_type(mock_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    with patch("foxcape.scraper.human_type") as mock_type:
        fox = Foxcape(default_config)
        fox.type_human("#email", "test@example.com")
        mock_type.assert_called_once()
    fox.close()


def test_get_with_wait_selector_and_turnstile(mock_camoufox: tuple) -> None:
    page, _ = mock_camoufox
    cfg = FoxcapeConfig(headless=True, solve_turnstile=True, simulate_mouse=False, human_delay_range=None)
    with patch("foxcape.scraper.solve_turnstile_if_present", return_value=True) as mock_ts:
        fox = Foxcape(cfg)
        result = fox.get(
            "https://example.com",
            wait_selector="#content",
            wait_until="networkidle",
            timeout_ms=5000,
            human_delay=False,
        )
        mock_ts.assert_called_once()
        page.wait_for_selector.assert_called_once_with("#content", timeout=5000)
        assert result.title == "Test Page"
    fox.close()


def test_close_swallows_page_errors(mock_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    page, cm = mock_camoufox
    page.close.side_effect = RuntimeError("already closed")
    cm.__exit__.side_effect = RuntimeError("exit failed")
    fox = Foxcape(default_config)
    fox.start()
    fox.close()
    assert fox.browser is None


def test_page_property_raises_when_no_page_context(monkeypatch: pytest.MonkeyPatch) -> None:
    browser = MagicMock()
    browser.pages = []
    browser.new_page = MagicMock(return_value=None)
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=browser)
    monkeypatch.setattr("foxcape.scraper.Camoufox", MagicMock(return_value=cm))
    fox = Foxcape(FoxcapeConfig(headless=True))
    with pytest.raises(BrowserStartupError, match="Failed to initialize browser page"):
        _ = fox.page
