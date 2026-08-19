"""Turnstile solving and human typing (mocked Playwright page)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foxcape.turnstile_and_typing import (
    async_human_type,
    async_solve_turnstile_if_present,
    human_type,
    solve_turnstile_if_present,
)


def _mock_keyboard() -> MagicMock:
    kb = MagicMock()
    kb.down = MagicMock()
    kb.up = MagicMock()
    kb.press = MagicMock()
    return kb


def _mock_locator(*, count: int = 1, visible: bool = True, bounding_box: dict | None = None) -> MagicMock:
    loc = MagicMock()
    loc.count.return_value = count
    loc.is_visible.return_value = visible
    loc.bounding_box.return_value = bounding_box
    loc.input_value.return_value = ""
    first = MagicMock()
    first.count.return_value = count
    first.is_visible.return_value = visible
    first.bounding_box.return_value = bounding_box
    first.input_value.return_value = ""
    loc.first = first
    return loc


def test_human_type_clicks_and_types_chars() -> None:
    page = MagicMock()
    element = MagicMock()
    page.locator.return_value.first = element
    page.keyboard = _mock_keyboard()
    with patch("foxcape.turnstile_and_typing.time.sleep"):
        with patch("foxcape.turnstile_and_typing.rng.uniform", return_value=0.05):
            with patch("foxcape.turnstile_and_typing.rng.rand_float", return_value=0.0):
                with patch("foxcape.turnstile_and_typing.rng.lognormvariate", return_value=0.05):
                    human_type(page, "#input", "ab", typo_probability=0.0)
    element.click.assert_called_once()
    assert page.keyboard.down.call_count == 2
    assert page.keyboard.up.call_count == 2


def test_human_type_generates_typo_and_backspace() -> None:
    page = MagicMock()
    page.locator.return_value.first = MagicMock()
    page.keyboard = _mock_keyboard()
    with patch("foxcape.turnstile_and_typing.time.sleep"):
        with patch("foxcape.turnstile_and_typing.rng.uniform", return_value=0.05):
            with patch("foxcape.turnstile_and_typing.rng.rand_float", return_value=0.01):
                with patch("foxcape.turnstile_and_typing.rng.choice", return_value="s"):
                    with patch("foxcape.turnstile_and_typing.rng.lognormvariate", return_value=0.05):
                        human_type(page, "#input", "a", typo_probability=1.0)
    page.keyboard.press.assert_any_call("s")
    page.keyboard.press.assert_any_call("Backspace")


@pytest.mark.asyncio
async def test_async_human_type() -> None:
    page = MagicMock()
    element = MagicMock()
    element.click = AsyncMock()
    page.locator.return_value.first = element
    page.keyboard = MagicMock()
    page.keyboard.down = AsyncMock()
    page.keyboard.up = AsyncMock()
    page.keyboard.press = AsyncMock()
    with patch("foxcape.turnstile_and_typing.asyncio.sleep", new_callable=AsyncMock):
        with patch("foxcape.turnstile_and_typing.rng.uniform", return_value=0.05):
            with patch("foxcape.turnstile_and_typing.rng.rand_float", return_value=0.0):
                with patch("foxcape.turnstile_and_typing.rng.lognormvariate", return_value=0.05):
                    await async_human_type(page, "#input", "x", typo_probability=0.0)
    element.click.assert_awaited_once()
    page.keyboard.down.assert_awaited_once_with("x")


def test_solve_turnstile_returns_false_when_no_iframe() -> None:
    page = MagicMock()
    page.locator.return_value = _mock_locator(count=0, visible=False)
    assert solve_turnstile_if_present(page) is False


def test_solve_turnstile_clicks_and_waits_for_resolution() -> None:
    page = MagicMock()
    page.viewport_size = {"width": 1280, "height": 800}
    page.mouse = MagicMock()
    iframe_loc = _mock_locator(count=1, visible=True, bounding_box={"x": 10, "y": 20, "width": 300, "height": 65})
    token_loc = _mock_locator(count=1, visible=True)
    token_loc.first.input_value.return_value = "token-abc"

    def locator_side_effect(sel: str):
        if "cf-turnstile-response" in sel:
            return token_loc
        return iframe_loc

    page.locator.side_effect = locator_side_effect

    with patch("foxcape.turnstile_and_typing.generate_windmouse_path", return_value=[(100.0, 100.0, 0.0)]):
        with patch("foxcape.turnstile_and_typing.time.sleep"):
            with patch("foxcape.turnstile_and_typing.rng.uniform", return_value=200.0):
                assert solve_turnstile_if_present(page, timeout_sec=0.1) is True
    page.mouse.down.assert_called_once()


def test_solve_turnstile_returns_false_on_exception() -> None:
    page = MagicMock()
    page.locator.side_effect = RuntimeError("broken")
    assert solve_turnstile_if_present(page) is False


@pytest.mark.asyncio
async def test_async_solve_turnstile_no_iframe() -> None:
    page = MagicMock()
    loc = _mock_locator(count=0)
    loc.count = AsyncMock(return_value=0)
    loc.is_visible = AsyncMock(return_value=False)
    loc.first.count = AsyncMock(return_value=0)
    loc.first.is_visible = AsyncMock(return_value=False)
    page.locator.return_value = loc
    assert await async_solve_turnstile_if_present(page) is False


@pytest.mark.asyncio
async def test_async_solve_turnstile_resolves_via_token() -> None:
    page = MagicMock()
    page.viewport_size = {"width": 1280, "height": 800}
    page.mouse = MagicMock()
    page.mouse.move = AsyncMock()
    page.mouse.down = AsyncMock()
    page.mouse.up = AsyncMock()

    iframe_loc = _mock_locator(count=1, visible=True, bounding_box={"x": 0, "y": 0, "width": 300, "height": 65})
    iframe_loc.count = AsyncMock(return_value=1)
    iframe_loc.is_visible = AsyncMock(return_value=True)
    iframe_loc.bounding_box = AsyncMock(return_value={"x": 0, "y": 0, "width": 300, "height": 65})
    iframe_loc.first.count = AsyncMock(return_value=1)
    iframe_loc.first.is_visible = AsyncMock(return_value=True)
    iframe_loc.first.bounding_box = AsyncMock(return_value={"x": 0, "y": 0, "width": 300, "height": 65})

    token_loc = MagicMock()
    token_loc.count = AsyncMock(return_value=1)
    token_loc.first.input_value = AsyncMock(return_value="resolved-token")

    def locator_side_effect(sel: str):
        if "cf-turnstile-response" in sel:
            return token_loc
        return iframe_loc

    page.locator.side_effect = locator_side_effect

    with patch("foxcape.turnstile_and_typing.generate_windmouse_path", return_value=[(50.0, 50.0, 0.0)]):
        with patch("foxcape.turnstile_and_typing.asyncio.sleep", new_callable=AsyncMock):
            with patch("foxcape.turnstile_and_typing.rng.uniform", return_value=200.0):
                assert await async_solve_turnstile_if_present(page, timeout_sec=0.1) is True
