"""AsyncFoxcape lifecycle and scrape path (mocked AsyncCamoufox)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foxcape import AsyncFoxcape, BrowserStartupError, FoxcapeConfig


async def test_async_context_manager_lifecycle(mock_async_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    page, cm = mock_async_camoufox
    async with AsyncFoxcape(default_config) as fox:
        assert fox.browser is not None
        active_page = await fox.get_page()
        assert active_page is page
    page.close.assert_called_once()
    cm.__aexit__.assert_called_once()


async def test_aget_returns_foxcape_result(mock_async_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    page, _ = mock_async_camoufox
    fox = AsyncFoxcape(default_config)
    result = await fox.get("https://example.com", human_delay=False, simulate_mouse=False)
    page.goto.assert_awaited_once()
    assert result.title == "Test Page"
    await fox.close()


async def test_afetch_classmethod(mock_async_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    result = await AsyncFoxcape.afetch("https://example.com", config=default_config, human_delay=False)
    assert result.title == "Test Page"


async def test_async_context_closes_browser_on_exception(
    mock_async_camoufox: tuple, default_config: FoxcapeConfig
) -> None:
    page, cm = mock_async_camoufox
    page.goto.side_effect = RuntimeError("navigation failed")
    with pytest.raises(RuntimeError, match="navigation failed"):
        async with AsyncFoxcape(default_config) as fox:
            await fox.get("https://example.com", human_delay=False)
    page.close.assert_called_once()
    cm.__aexit__.assert_awaited_once()


async def test_async_start_is_idempotent(mock_async_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    _, cm = mock_async_camoufox
    fox = AsyncFoxcape(default_config)
    await fox.start()
    await fox.start()
    cm.__aenter__.assert_awaited_once()


async def test_aevaluate_with_and_without_arg(mock_async_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    page, _ = mock_async_camoufox
    page.evaluate = AsyncMock(return_value="ok")
    fox = AsyncFoxcape(default_config)
    assert await fox.aevaluate("window.location.href") == "ok"
    assert await fox.aevaluate("fn", {"a": 1}) == "ok"
    await fox.close()


async def test_type_human_async(mock_async_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    with patch("foxcape.async_scraper.async_human_type", new_callable=AsyncMock) as mock_type:
        fox = AsyncFoxcape(default_config)
        await fox.type_human("#field", "hello")
        mock_type.assert_awaited_once()
    await fox.close()


async def test_get_with_turnstile_and_wait_selector(mock_async_camoufox: tuple) -> None:
    page, _ = mock_async_camoufox
    cfg = FoxcapeConfig(headless=True, solve_turnstile=True, simulate_mouse=False, human_delay_range=None)
    with patch("foxcape.async_scraper.async_solve_turnstile_if_present", new_callable=AsyncMock) as mock_ts:
        fox = AsyncFoxcape(cfg)
        result = await fox.get("https://example.com", wait_selector="h1", human_delay=False)
        mock_ts.assert_awaited_once()
        page.wait_for_selector.assert_awaited_once()
        assert result.title == "Test Page"
    await fox.close()


async def test_async_start_raises_browser_startup_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingCamoufox:
        def __init__(self, *_args, **_kwargs):
            pass

        async def __aenter__(self):
            raise RuntimeError("async browser missing")

        async def __aexit__(self, *_args):
            return False

    monkeypatch.setattr("foxcape.async_scraper.AsyncCamoufox", FailingCamoufox)
    fox = AsyncFoxcape(FoxcapeConfig(headless=True))
    with pytest.raises(BrowserStartupError, match="camoufox fetch"):
        await fox.start()


async def test_async_start_propagates_config_errors_without_browser_startup_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "foxcape.async_scraper.build_camoufox_kwargs",
        MagicMock(side_effect=ValueError("invalid proxy URL")),
    )
    fox = AsyncFoxcape(FoxcapeConfig(headless=True))
    with pytest.raises(ValueError, match="invalid proxy URL"):
        await fox.start()


async def test_async_start_cleans_up_browser_when_page_setup_fails(
    mock_async_camoufox: tuple, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, cm = mock_async_camoufox
    monkeypatch.setattr(
        "foxcape.async_scraper.inject_async_page_evasions",
        AsyncMock(side_effect=RuntimeError("evasion inject failed")),
    )
    fox = AsyncFoxcape(FoxcapeConfig(headless=True))
    with pytest.raises(RuntimeError, match="evasion inject failed"):
        await fox.start()
    cm.__aexit__.assert_awaited_once()
    assert fox.browser is None
    assert fox._camoufox_cm is None
