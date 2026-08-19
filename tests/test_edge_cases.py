"""Edge-case coverage for remaining branches."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foxcape.async_scraper import AsyncFoxcape
from foxcape.cadence import MarkovCadence
from foxcape.camoufox_launch import async_resolve_initial_page
from foxcape.config import FoxcapeConfig
from foxcape.profiles import ProfileManager
from foxcape.rng import choice, choices, lognormvariate
from foxcape.scrape_cadence import apply_async_human_cadence
from foxcape.scraper import Foxcape


def test_rng_helpers_return_values() -> None:
    assert 1 <= choice([1, 2, 3]) <= 3
    assert choices([1, 2], [0.5, 0.5])
    assert lognormvariate(0.0, 0.5) > 0


def test_markov_cadence_hesitate_and_prepare_durations() -> None:
    with patch("foxcape.cadence.rng.uniform", side_effect=[0.5, 1.5, 0.4, 0.3, 0.2]):
        with patch("foxcape.cadence.rng.choices", side_effect=[["HESITATE"], ["PREPARE_NEXT"], ["DONE"]]):
            sequence = MarkovCadence.generate_behavioral_sequence(max_steps=4)
    states = [s for s, _ in sequence]
    assert "HESITATE" in states or "PREPARE_NEXT" in states


@pytest.mark.asyncio
async def test_async_resolve_initial_page_reuses_existing() -> None:
    page = MagicMock()
    browser = MagicMock(pages=[page])
    assert await async_resolve_initial_page(browser) is page


@pytest.mark.asyncio
async def test_async_human_cadence_markov_delay_only() -> None:
    page = MagicMock()
    page.content = AsyncMock(return_value="<html><body>words</body></html>")
    cfg = FoxcapeConfig(use_markov_cadence=True, human_delay_range=(0.5, 2.0))
    with patch("foxcape.scrape_cadence.MarkovCadence.calculate_reading_dwell_time", return_value=0.7):
        with patch("foxcape.scrape_cadence.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await apply_async_human_cadence(page, cfg, simulate_mouse=False, human_delay=True)
    mock_sleep.assert_awaited_once_with(0.7)


@pytest.mark.asyncio
async def test_async_close_swallows_errors(mock_async_camoufox: tuple, default_config: FoxcapeConfig) -> None:
    page, cm = mock_async_camoufox
    page.close = AsyncMock(side_effect=RuntimeError("closed"))
    cm.__aexit__ = AsyncMock(side_effect=RuntimeError("exit"))
    fox = AsyncFoxcape(default_config)
    await fox.start()
    await fox.close()
    assert fox.browser is None


def test_sync_get_raises_when_page_missing_after_start(monkeypatch: pytest.MonkeyPatch) -> None:
    browser = MagicMock()
    browser.pages = []
    browser.new_page = MagicMock(return_value=None)
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=browser)
    monkeypatch.setattr("foxcape.scraper.Camoufox", MagicMock(return_value=cm))
    fox = Foxcape(FoxcapeConfig(headless=True))
    with pytest.raises(Exception, match="Failed to acquire page context"):
        fox.get("https://example.com", human_delay=False)


def test_profile_clean_lock_swallows_unlink_error(tmp_path) -> None:
    profile = ProfileManager.get_or_create("lock_err", profiles_dir=tmp_path)
    lock = profile.profile_dir / "parent.lock"
    lock.write_text("x", encoding="utf-8")
    with patch.object(Path, "unlink", side_effect=PermissionError("denied")):
        profile.clean_lock()


def test_profile_age_days_zero_when_no_created_at(tmp_path) -> None:
    profile = ProfileManager.get_or_create("no_date", profiles_dir=tmp_path)
    profile.metadata.pop("created_at", None)
    assert profile.age_days == 0.0
