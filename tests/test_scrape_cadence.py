"""Human cadence application after navigation (sync + async)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foxcape.config import FoxcapeConfig
from foxcape.scrape_cadence import apply_async_human_cadence, apply_sync_human_cadence


def test_sync_markov_cadence_with_mouse() -> None:
    page = MagicMock()
    page.content.return_value = "<html><body><p>content</p></body></html>"
    cfg = FoxcapeConfig(use_markov_cadence=True, human_delay_range=(0.5, 2.0), simulate_mouse=True)
    with patch("foxcape.scrape_cadence.MarkovCadence.calculate_reading_dwell_time", return_value=1.2):
        with patch("foxcape.scrape_cadence.perform_human_activity") as mock_activity:
            apply_sync_human_cadence(page, cfg, simulate_mouse=True, human_delay=True)
    mock_activity.assert_called_once_with(page, max_duration_sec=1.2)


def test_sync_markov_cadence_delay_only() -> None:
    page = MagicMock()
    page.content.return_value = "<html></html>"
    cfg = FoxcapeConfig(use_markov_cadence=True, human_delay_range=(0.5, 2.0))
    with patch("foxcape.scrape_cadence.MarkovCadence.calculate_reading_dwell_time", return_value=0.9):
        with patch("foxcape.scrape_cadence.time.sleep") as mock_sleep:
            apply_sync_human_cadence(page, cfg, simulate_mouse=False, human_delay=True)
    mock_sleep.assert_called_once_with(0.9)


def test_sync_simple_mouse_without_markov() -> None:
    page = MagicMock()
    cfg = FoxcapeConfig(use_markov_cadence=False, human_delay_range=(1.0, 2.0))
    with patch("foxcape.scrape_cadence.rng.uniform", return_value=1.5):
        with patch("foxcape.scrape_cadence.perform_human_activity") as mock_activity:
            apply_sync_human_cadence(page, cfg, simulate_mouse=True, human_delay=False)
    mock_activity.assert_called_once_with(page, max_duration_sec=1.5)


def test_sync_human_delay_only() -> None:
    page = MagicMock()
    cfg = FoxcapeConfig(use_markov_cadence=False, human_delay_range=(0.3, 0.7))
    with patch("foxcape.scrape_cadence.rng.uniform", return_value=0.5):
        with patch("foxcape.scrape_cadence.time.sleep") as mock_sleep:
            apply_sync_human_cadence(page, cfg, simulate_mouse=False, human_delay=True)
    mock_sleep.assert_called_once_with(0.5)


def test_sync_no_op_when_all_disabled() -> None:
    page = MagicMock()
    cfg = FoxcapeConfig(use_markov_cadence=False, human_delay_range=(0.5, 2.0))
    with patch("foxcape.scrape_cadence.time.sleep") as mock_sleep:
        with patch("foxcape.scrape_cadence.perform_human_activity") as mock_activity:
            apply_sync_human_cadence(page, cfg, simulate_mouse=False, human_delay=False)
    mock_sleep.assert_not_called()
    mock_activity.assert_not_called()


@pytest.mark.asyncio
async def test_async_markov_cadence_with_mouse() -> None:
    page = MagicMock()
    page.content = AsyncMock(return_value="<html><body>text</body></html>")
    cfg = FoxcapeConfig(use_markov_cadence=True, human_delay_range=(0.5, 2.0))
    with patch("foxcape.scrape_cadence.MarkovCadence.calculate_reading_dwell_time", return_value=1.0):
        with patch("foxcape.scrape_cadence.async_perform_human_activity", new_callable=AsyncMock) as mock_activity:
            await apply_async_human_cadence(page, cfg, simulate_mouse=True, human_delay=True)
    mock_activity.assert_awaited_once_with(page, max_duration_sec=1.0)


@pytest.mark.asyncio
async def test_async_human_delay_only() -> None:
    page = MagicMock()
    cfg = FoxcapeConfig(use_markov_cadence=False, human_delay_range=(0.2, 0.4))
    with patch("foxcape.scrape_cadence.rng.uniform", return_value=0.3):
        with patch("foxcape.scrape_cadence.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await apply_async_human_cadence(page, cfg, simulate_mouse=False, human_delay=True)
    mock_sleep.assert_awaited_once_with(0.3)
