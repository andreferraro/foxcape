import itertools

import pytest

from foxcape.cadence import MarkovCadence
from foxcape.humanizer import (
    async_perform_human_activity,
    async_simulate_human_mouse_movement,
    generate_windmouse_path,
    perform_human_activity,
    simulate_human_mouse_movement,
)
from foxcape.turnstile_and_typing import (
    async_human_type,
    async_solve_turnstile_if_present,
    human_type,
    solve_turnstile_if_present,
)


class Mouse:
    def __init__(self) -> None:
        self.moves: list[tuple[float, float]] = []
        self.wheels: list[tuple[int, int]] = []
        self.downs = 0
        self.ups = 0

    def move(self, x: float, y: float) -> None:
        self.moves.append((x, y))

    def wheel(self, x: int, y: int) -> None:
        self.wheels.append((x, y))

    def down(self) -> None:
        self.downs += 1

    def up(self) -> None:
        self.ups += 1


class AsyncMouse(Mouse):
    async def move(self, x: float, y: float) -> None:
        self.moves.append((x, y))

    async def wheel(self, x: int, y: int) -> None:
        self.wheels.append((x, y))

    async def down(self) -> None:
        self.downs += 1

    async def up(self) -> None:
        self.ups += 1


class Keyboard:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def press(self, key: str) -> None:
        self.events.append(("press", key))

    def down(self, key: str) -> None:
        self.events.append(("down", key))

    def up(self, key: str) -> None:
        self.events.append(("up", key))


class AsyncKeyboard(Keyboard):
    async def press(self, key: str) -> None:
        self.events.append(("press", key))

    async def down(self, key: str) -> None:
        self.events.append(("down", key))

    async def up(self, key: str) -> None:
        self.events.append(("up", key))


class Locator:
    first: "Locator"

    def __init__(self) -> None:
        self.first = self
        self.clicked = False

    def click(self) -> None:
        self.clicked = True


class AsyncLocator(Locator):
    async def click(self) -> None:
        self.clicked = True


class Page:
    viewport_size = {"width": 1280, "height": 800}

    def __init__(self) -> None:
        self.mouse = Mouse()
        self.keyboard = Keyboard()
        self.locator_obj = Locator()

    def locator(self, selector: str) -> Locator:
        assert selector == "#field"
        return self.locator_obj


class AsyncPage(Page):
    def __init__(self) -> None:
        self.mouse = AsyncMouse()
        self.keyboard = AsyncKeyboard()
        self.locator_obj = AsyncLocator()


def test_markov_dwell_and_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("foxcape.cadence.rng.paretovariate", lambda alpha: 1.0)
    monkeypatch.setattr("foxcape.cadence.rng.choices", lambda choices, weights: [choices[-1]])

    assert MarkovCadence.calculate_reading_dwell_time("hello", min_seconds=0.5, max_seconds=2.0) == 0.9
    assert MarkovCadence.generate_behavioral_sequence(max_steps=3)[0][0] == "SCAN_HEADER"


def test_humanizer_mouse_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("foxcape.humanizer.time.sleep", lambda _: None)
    monkeypatch.setattr("foxcape.humanizer.generate_windmouse_path", lambda *args, **kwargs: [(1, 2, 0), (3, 4, 0)])

    page = Page()
    path = generate_windmouse_path(0, 0, 3, 4)
    assert path[-1][:2] == (3, 4)

    simulate_human_mouse_movement(page, 10, 20)  # type: ignore[arg-type]
    assert page.mouse.moves == [(1, 2), (3, 4)]


def test_perform_human_activity(monkeypatch: pytest.MonkeyPatch) -> None:
    times = iter([0.0, 0.0, 0.1, 1.0])
    monkeypatch.setattr("foxcape.humanizer.time.time", lambda: next(times))
    monkeypatch.setattr("foxcape.humanizer.time.sleep", lambda _: None)
    monkeypatch.setattr("foxcape.humanizer.simulate_human_mouse_movement", lambda page, x, y: None)
    monkeypatch.setattr("foxcape.humanizer.rng.rand_float", lambda: 0.2)
    monkeypatch.setattr("foxcape.humanizer.rng.randint", lambda a, b: 80)

    page = Page()
    perform_human_activity(page, max_duration_sec=0.5)  # type: ignore[arg-type]
    assert page.mouse.wheels


async def test_async_humanizer_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "foxcape.humanizer.generate_windmouse_path",
        lambda *args, **kwargs: [(1, 2, 0), (3, 4, 0)],
    )
    sleeps: list[float] = []

    async def fake_sleep(delay: float) -> None:
        sleeps.append(delay)

    monkeypatch.setattr("foxcape.humanizer.asyncio.sleep", fake_sleep)

    page = AsyncPage()
    await async_simulate_human_mouse_movement(page, 10, 20)  # type: ignore[arg-type]
    assert page.mouse.moves == [(1, 2), (3, 4)]


async def test_async_perform_human_activity(monkeypatch: pytest.MonkeyPatch) -> None:
    times = itertools.chain([0.0, 0.0, 0.1, 1.0])
    monkeypatch.setattr("foxcape.humanizer.time.time", lambda: next(times))
    monkeypatch.setattr("foxcape.humanizer.async_simulate_human_mouse_movement", lambda page, x, y: None)
    monkeypatch.setattr("foxcape.humanizer.rng.rand_float", lambda: 0.2)
    monkeypatch.setattr("foxcape.humanizer.rng.randint", lambda a, b: 80)

    async def fake_sleep(delay: float) -> None:
        return None

    async def fake_move(page: AsyncPage, x: float, y: float) -> None:
        return None

    monkeypatch.setattr("foxcape.humanizer.async_simulate_human_mouse_movement", fake_move)
    monkeypatch.setattr("foxcape.humanizer.asyncio.sleep", fake_sleep)

    page = AsyncPage()
    await async_perform_human_activity(page, max_duration_sec=0.5)  # type: ignore[arg-type]
    assert page.mouse.wheels


def test_human_type_without_typos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("foxcape.turnstile_and_typing.time.sleep", lambda _: None)
    monkeypatch.setattr("foxcape.turnstile_and_typing.rng.uniform", lambda a, b: 0.05)
    monkeypatch.setattr("foxcape.turnstile_and_typing.rng.rand_float", lambda: 1.0)
    monkeypatch.setattr("foxcape.turnstile_and_typing.rng.lognormvariate", lambda mu, sigma: 0.01)

    page = Page()
    human_type(page, "#field", "Ab", typo_probability=0.0)  # type: ignore[arg-type]
    assert page.locator_obj.clicked is True
    assert ("down", "A") in page.keyboard.events
    assert ("up", "b") in page.keyboard.events


async def test_async_human_type_with_typo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("foxcape.turnstile_and_typing.rng.uniform", lambda a, b: 0.05)
    monkeypatch.setattr("foxcape.turnstile_and_typing.rng.rand_float", lambda: 0.0)
    monkeypatch.setattr("foxcape.turnstile_and_typing.rng.choice", lambda items: items[0])
    monkeypatch.setattr("foxcape.turnstile_and_typing.rng.lognormvariate", lambda mu, sigma: 0.01)

    async def fake_sleep(delay: float) -> None:
        return None

    monkeypatch.setattr("foxcape.turnstile_and_typing.asyncio.sleep", fake_sleep)

    page = AsyncPage()
    await async_human_type(page, "#field", "A", typo_probability=1.0)  # type: ignore[arg-type]
    assert ("press", "Q") in page.keyboard.events
    assert ("press", "Backspace") in page.keyboard.events
    assert ("down", "A") in page.keyboard.events


class TurnstileLocator:
    first: "TurnstileLocator"

    def __init__(self, *, visible: bool = True, token: str = "token", box: dict | None = None) -> None:
        self.first = self
        self.visible = visible
        self.token = token
        self.box = box if box is not None else {"x": 10, "y": 20, "width": 80, "height": 40}

    def count(self) -> int:
        return 1

    def is_visible(self, timeout: int = 0) -> bool:
        return self.visible

    def bounding_box(self, timeout: int = 0) -> dict | None:
        return self.box

    def input_value(self, timeout: int = 0) -> str:
        return self.token


class AsyncTurnstileLocator(TurnstileLocator):
    async def count(self) -> int:
        return 1

    async def is_visible(self, timeout: int = 0) -> bool:
        return self.visible

    async def bounding_box(self, timeout: int = 0) -> dict | None:
        return self.box

    async def input_value(self, timeout: int = 0) -> str:
        return self.token


class TurnstilePage(Page):
    def __init__(self, iframe: TurnstileLocator | None) -> None:
        super().__init__()
        self.iframe = iframe
        self.token = TurnstileLocator(token="solved")

    def locator(self, selector: str) -> TurnstileLocator:
        if selector == 'input[name="cf-turnstile-response"]':
            return self.token
        return self.iframe or TurnstileLocator(visible=False, token="", box=None)


class AsyncTurnstilePage(AsyncPage):
    def __init__(self, iframe: AsyncTurnstileLocator | None) -> None:
        super().__init__()
        self.iframe = iframe
        self.token = AsyncTurnstileLocator(token="solved")

    def locator(self, selector: str) -> AsyncTurnstileLocator:
        if selector == 'input[name="cf-turnstile-response"]':
            return self.token
        return self.iframe or AsyncTurnstileLocator(visible=False, token="", box=None)


def test_solve_turnstile_if_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("foxcape.turnstile_and_typing.generate_windmouse_path", lambda *args, **kwargs: [(1, 2, 0)])
    monkeypatch.setattr("foxcape.turnstile_and_typing.time.sleep", lambda _: None)
    monkeypatch.setattr("foxcape.turnstile_and_typing.time.time", iter([0.0, 0.0]).__next__)

    page = TurnstilePage(TurnstileLocator())
    assert solve_turnstile_if_present(page, timeout_sec=1.0) is True  # type: ignore[arg-type]
    assert page.mouse.downs == 1
    assert page.mouse.ups == 1


def test_solve_turnstile_returns_false_without_visible_iframe() -> None:
    assert solve_turnstile_if_present(TurnstilePage(None), timeout_sec=0.1) is False  # type: ignore[arg-type]


async def test_async_solve_turnstile_if_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("foxcape.turnstile_and_typing.generate_windmouse_path", lambda *args, **kwargs: [(1, 2, 0)])
    monkeypatch.setattr("foxcape.turnstile_and_typing.time.time", iter([0.0, 0.0]).__next__)

    async def fake_sleep(delay: float) -> None:
        return None

    monkeypatch.setattr("foxcape.turnstile_and_typing.asyncio.sleep", fake_sleep)

    page = AsyncTurnstilePage(AsyncTurnstileLocator())
    assert await async_solve_turnstile_if_present(page, timeout_sec=1.0) is True  # type: ignore[arg-type]
    assert page.mouse.downs == 1
    assert page.mouse.ups == 1
