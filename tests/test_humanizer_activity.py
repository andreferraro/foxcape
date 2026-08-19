"""Humanizer mouse simulation and organic activity (mocked Playwright page)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foxcape.humanizer import (
    async_perform_human_activity,
    async_simulate_human_mouse_movement,
    perform_human_activity,
    simulate_human_mouse_movement,
)


def _mock_page() -> MagicMock:
    page = MagicMock()
    page.viewport_size = {"width": 1280, "height": 800}
    page.mouse = MagicMock()
    return page


def test_simulate_human_mouse_movement_moves_along_path() -> None:
    page = _mock_page()
    with patch("foxcape.humanizer.generate_windmouse_path", return_value=[(100.0, 100.0, 0.01), (200.0, 150.0, 0.0)]):
        simulate_human_mouse_movement(page, 200.0, 150.0)
    assert page.mouse.move.call_count == 2
    page.mouse.move.assert_any_call(100.0, 100.0)
    page.mouse.move.assert_any_call(200.0, 150.0)


@pytest.mark.asyncio
async def test_async_simulate_human_mouse_movement() -> None:
    page = _mock_page()
    page.mouse.move = AsyncMock()
    with patch("foxcape.humanizer.generate_windmouse_path", return_value=[(50.0, 50.0, 0.0), (300.0, 200.0, 0.0)]):
        await async_simulate_human_mouse_movement(page, 300.0, 200.0)
    assert page.mouse.move.await_count == 2


def test_perform_human_activity_runs_within_duration() -> None:
    page = _mock_page()
    with patch("foxcape.humanizer.time.time", side_effect=[0.0, 0.0, 2.5]):
        with patch("foxcape.humanizer.simulate_human_mouse_movement") as mock_move:
            with patch("foxcape.humanizer.rng.uniform", return_value=0.2):
                with patch("foxcape.humanizer.rng.rand_float", return_value=0.1):
                    perform_human_activity(page, max_duration_sec=2.0)
    mock_move.assert_called()


def test_perform_human_activity_scrolls_occasionally() -> None:
    page = _mock_page()
    with patch("foxcape.humanizer.time.time", side_effect=[0.0, 0.0, 3.0]):
        with patch("foxcape.humanizer.simulate_human_mouse_movement"):
            with patch("foxcape.humanizer.rng.uniform", return_value=0.2):
                with patch("foxcape.humanizer.rng.rand_float", side_effect=[0.3, 0.1]):
                    with patch("foxcape.humanizer.rng.randint", return_value=80):
                        perform_human_activity(page, max_duration_sec=2.0)
    page.mouse.wheel.assert_called()


@pytest.mark.asyncio
async def test_async_perform_human_activity() -> None:
    page = _mock_page()
    page.mouse.move = AsyncMock()
    page.mouse.wheel = AsyncMock()
    with patch("foxcape.humanizer.time.time", side_effect=[0.0, 0.0, 3.0]):
        with patch("foxcape.humanizer.async_simulate_human_mouse_movement", new_callable=AsyncMock):
            with patch("foxcape.humanizer.rng.uniform", return_value=0.1):
                with patch("foxcape.humanizer.rng.rand_float", return_value=0.9):
                    await async_perform_human_activity(page, max_duration_sec=1.0)
