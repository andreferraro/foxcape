import asyncio
import math
import time

from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage

from . import rng
from .humanizer import generate_windmouse_path

CF_TURNSTILE_RESPONSE_SELECTOR = 'input[name="cf-turnstile-response"]'
CF_TURNSTILE_IFRAME_SELECTORS = (
    'iframe[src*="challenges.cloudflare.com"]',
    'iframe[src*="turnstile"]',
    "#turnstile-wrapper iframe",
    "#cf-turnstile-wrapper iframe",
)

KEYBOARD_NEIGHBORS = {
    "a": ["q", "w", "s", "z"],
    "b": ["v", "g", "h", "n"],
    "c": ["x", "d", "f", "v"],
    "d": ["s", "e", "r", "f", "x", "c"],
    "e": ["w", "s", "d", "r", "3", "4"],
    "f": ["d", "r", "t", "g", "c", "v"],
    "g": ["f", "t", "y", "h", "v", "b"],
    "h": ["g", "y", "u", "j", "b", "n"],
    "i": ["u", "j", "k", "o", "8", "9"],
    "j": ["h", "u", "i", "k", "n", "m"],
    "k": ["j", "i", "o", "l", "m"],
    "l": ["k", "o", "p"],
    "m": ["n", "j", "k"],
    "n": ["b", "h", "j", "m"],
    "o": ["i", "k", "l", "p", "9", "0"],
    "p": ["o", "l", "0"],
    "q": ["1", "2", "w", "a"],
    "r": ["e", "d", "f", "t", "4", "5"],
    "s": ["a", "w", "e", "d", "x", "z"],
    "t": ["r", "f", "g", "y", "5", "6"],
    "u": ["y", "h", "j", "i", "7", "8"],
    "v": ["c", "f", "g", "b"],
    "w": ["q", "a", "s", "e", "2", "3"],
    "x": ["z", "s", "d", "c"],
    "y": ["t", "g", "h", "u", "6", "7"],
    "z": ["a", "s", "x"],
}


def human_type(
    page: SyncPage,
    selector: str,
    text: str,
    typo_probability: float = 0.04,
    wpm_speed: float = 65.0,
):
    """
    Types text with authentic human biometric rhythm:
    - Log-normal inter-key flight time.
    - Key dwell time (press down -> release).
    - Natural typo generation with immediate Backspace correction.
    """
    element = page.locator(selector).first
    element.click()
    time.sleep(rng.uniform(0.1, 0.3))

    base_delay = 60.0 / (wpm_speed * 5.0)

    for char in text:
        lower_char = char.lower()
        if typo_probability > 0 and lower_char in KEYBOARD_NEIGHBORS and rng.rand_float() < typo_probability:
            typo_char = rng.choice(KEYBOARD_NEIGHBORS[lower_char])
            if char.isupper():
                typo_char = typo_char.upper()

            page.keyboard.press(typo_char)
            time.sleep(rng.uniform(0.08, 0.25))
            page.keyboard.press("Backspace")
            time.sleep(rng.uniform(0.06, 0.18))

        dwell_ms = rng.uniform(40, 110) / 1000.0
        page.keyboard.down(char)
        time.sleep(dwell_ms)
        page.keyboard.up(char)

        flight_delay = rng.lognormvariate(math.log(base_delay), 0.35)
        time.sleep(max(0.03, min(0.4, flight_delay)))


async def async_human_type(
    page: AsyncPage,
    selector: str,
    text: str,
    typo_probability: float = 0.04,
    wpm_speed: float = 65.0,
):
    """
    Asynchronously types text with authentic human biometric rhythm.
    """
    element = page.locator(selector).first
    await element.click()
    await asyncio.sleep(rng.uniform(0.1, 0.3))

    base_delay = 60.0 / (wpm_speed * 5.0)

    for char in text:
        lower_char = char.lower()
        if typo_probability > 0 and lower_char in KEYBOARD_NEIGHBORS and rng.rand_float() < typo_probability:
            typo_char = rng.choice(KEYBOARD_NEIGHBORS[lower_char])
            if char.isupper():
                typo_char = typo_char.upper()

            await page.keyboard.press(typo_char)
            await asyncio.sleep(rng.uniform(0.08, 0.25))
            await page.keyboard.press("Backspace")
            await asyncio.sleep(rng.uniform(0.06, 0.18))

        dwell_ms = rng.uniform(40, 110) / 1000.0
        await page.keyboard.down(char)
        await asyncio.sleep(dwell_ms)
        await page.keyboard.up(char)

        flight_delay = rng.lognormvariate(math.log(base_delay), 0.35)
        await asyncio.sleep(max(0.03, min(0.4, flight_delay)))


def _find_turnstile_iframe_sync(page: SyncPage):
    for sel in CF_TURNSTILE_IFRAME_SELECTORS:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible(timeout=400):
                return loc
        except Exception:
            continue
    return None


async def _find_turnstile_iframe_async(page: AsyncPage):
    for sel in CF_TURNSTILE_IFRAME_SELECTORS:
        loc = page.locator(sel).first
        try:
            if await loc.count() > 0 and await loc.is_visible(timeout=400):
                return loc
        except Exception:
            continue
    return None


def _click_turnstile_target_sync(page: SyncPage, box: dict) -> None:
    target_x = box["x"] + min(35.0, box["width"] / 2.0)
    target_y = box["y"] + (box["height"] / 2.0)
    vp = page.viewport_size or {"width": 1280, "height": 800}
    path = generate_windmouse_path(
        start_x=rng.uniform(100, vp["width"] - 100),
        start_y=rng.uniform(100, vp["height"] - 100),
        dest_x=target_x,
        dest_y=target_y,
    )
    for x, y, delay in path:
        page.mouse.move(x, y)
        if delay > 0:
            time.sleep(delay)
    time.sleep(rng.uniform(0.1, 0.25))
    page.mouse.down()
    time.sleep(rng.uniform(0.06, 0.12))
    page.mouse.up()


async def _click_turnstile_target_async(page: AsyncPage, box: dict) -> None:
    target_x = box["x"] + min(35.0, box["width"] / 2.0)
    target_y = box["y"] + (box["height"] / 2.0)
    vp = page.viewport_size or {"width": 1280, "height": 800}
    path = generate_windmouse_path(
        start_x=rng.uniform(100, vp["width"] - 100),
        start_y=rng.uniform(100, vp["height"] - 100),
        dest_x=target_x,
        dest_y=target_y,
    )
    for x, y, delay in path:
        await page.mouse.move(x, y)
        if delay > 0:
            await asyncio.sleep(delay)
    await asyncio.sleep(rng.uniform(0.1, 0.25))
    await page.mouse.down()
    await asyncio.sleep(rng.uniform(0.06, 0.12))
    await page.mouse.up()


def _is_turnstile_resolved_sync(page: SyncPage, turnstile_iframe) -> bool:
    token_locator = page.locator(CF_TURNSTILE_RESPONSE_SELECTOR)
    if token_locator.count() > 0:
        token_val = token_locator.first.input_value(timeout=300)
        if token_val:
            return True
    return not turnstile_iframe.is_visible(timeout=300)


async def _is_turnstile_resolved_async(page: AsyncPage, turnstile_iframe) -> bool:
    token_locator = page.locator(CF_TURNSTILE_RESPONSE_SELECTOR)
    if await token_locator.count() > 0:
        token_val = await token_locator.first.input_value(timeout=300)
        if token_val:
            return True
    return not await turnstile_iframe.is_visible(timeout=300)


def _wait_turnstile_resolution_sync(page: SyncPage, turnstile_iframe, timeout_sec: float) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        time.sleep(0.4)
        if _is_turnstile_resolved_sync(page, turnstile_iframe):
            return True
    return False


async def _wait_turnstile_resolution_async(page: AsyncPage, turnstile_iframe, timeout_sec: float) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        await asyncio.sleep(0.4)
        if await _is_turnstile_resolved_async(page, turnstile_iframe):
            return True
    return False


def solve_turnstile_if_present(page: SyncPage, timeout_sec: float = 5.0) -> bool:
    """
    Non-blocking detection of Cloudflare Turnstile / Challenge iframes.
    If present, moves mouse organically with WindMouse and clicks.
    """
    try:
        turnstile_iframe = _find_turnstile_iframe_sync(page)
        if not turnstile_iframe:
            return False

        box = turnstile_iframe.bounding_box(timeout=500)
        if not box:
            return False

        _click_turnstile_target_sync(page, box)
        return _wait_turnstile_resolution_sync(page, turnstile_iframe, timeout_sec)
    except Exception:
        return False


async def async_solve_turnstile_if_present(page: AsyncPage, timeout_sec: float = 5.0) -> bool:
    """
    Non-blocking async detection of Cloudflare Turnstile / Challenge iframes.
    """
    try:
        turnstile_iframe = await _find_turnstile_iframe_async(page)
        if not turnstile_iframe:
            return False

        box = await turnstile_iframe.bounding_box(timeout=500)
        if not box:
            return False

        await _click_turnstile_target_async(page, box)
        return await _wait_turnstile_resolution_async(page, turnstile_iframe, timeout_sec)
    except Exception:
        return False
