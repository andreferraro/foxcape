import asyncio
import math
import time

from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage

from . import rng


def generate_windmouse_path(
    start_x: float,
    start_y: float,
    dest_x: float,
    dest_y: float,
    gravity: float = 9.0,
    wind: float = 3.0,
    min_wait: float = 2.0,
    max_wait: float = 8.0,
    max_step: float = 10.0,
    target_area: float = 15.0,
) -> list[tuple[float, float, float]]:
    """
    Generates human-like mouse trajectory using the WindMouse algorithm (Fitts's Law + Inertia + Micro-tremors).
    Returns list of (x, y, sleep_time_ms).
    """
    points = []
    current_x, current_y = start_x, start_y
    v_x, v_y = 0.0, 0.0
    w_x, w_y = 0.0, 0.0

    dist = math.hypot(dest_x - start_x, dest_y - start_y)

    while True:
        dist = math.hypot(dest_x - current_x, dest_y - current_y)
        if dist < 1.0:
            break

        w_mag = min(wind, dist)
        if dist >= target_area:
            w_x = w_x / math.sqrt(3) + (rng.rand_float() * (w_mag * 2 + 1) - w_mag) / math.sqrt(5)
            w_y = w_y / math.sqrt(3) + (rng.rand_float() * (w_mag * 2 + 1) - w_mag) / math.sqrt(5)
        else:
            w_x /= math.sqrt(3)
            w_y /= math.sqrt(3)
            if max_step < 3:
                max_step = rng.rand_float() * 3 + 3.0
            else:
                max_step /= math.sqrt(5)

        v_x += w_x + (gravity * (dest_x - current_x)) / dist
        v_y += w_y + (gravity * (dest_y - current_y)) / dist

        v_mag = math.hypot(v_x, v_y)
        if v_mag > max_step:
            v_clip = (max_step / 2.0) + rng.rand_float() * (max_step / 2.0)
            v_x = (v_x / v_mag) * v_clip
            v_y = (v_y / v_mag) * v_clip

        current_x += v_x
        current_y += v_y

        jitter_x = rng.gauss(0, 0.3)
        jitter_y = rng.gauss(0, 0.3)

        step_delay = (rng.uniform(min_wait, max_wait)) / 1000.0
        points.append((round(current_x + jitter_x, 1), round(current_y + jitter_y, 1), step_delay))

    points.append((dest_x, dest_y, rng.uniform(5, 15) / 1000.0))
    return points


def simulate_human_mouse_movement(page: SyncPage, target_x: float, target_y: float):
    """Simulates realistic human trajectory towards a target coordinate."""
    vp = page.viewport_size or {"width": 1280, "height": 800}
    start_x = rng.uniform(100, vp["width"] - 100)
    start_y = rng.uniform(100, vp["height"] - 100)

    path = generate_windmouse_path(start_x, start_y, target_x, target_y)
    for x, y, delay in path:
        page.mouse.move(x, y)
        if delay > 0:
            time.sleep(delay)


async def async_simulate_human_mouse_movement(page: AsyncPage, target_x: float, target_y: float):
    """Asynchronously simulates realistic human trajectory towards a target coordinate."""
    vp = page.viewport_size or {"width": 1280, "height": 800}
    start_x = rng.uniform(100, vp["width"] - 100)
    start_y = rng.uniform(100, vp["height"] - 100)

    path = generate_windmouse_path(start_x, start_y, target_x, target_y)
    for x, y, delay in path:
        await page.mouse.move(x, y)
        if delay > 0:
            await asyncio.sleep(delay)


def perform_human_activity(page: SyncPage, max_duration_sec: float = 2.0):
    """
    Simulates organic human browsing behavior:
    1. Smooth realistic mouse wandering (WindMouse).
    2. Subtle micro-scrolling.
    3. Natural pause intervals.
    """
    vp = page.viewport_size or {"width": 1280, "height": 800}
    start_time = time.time()

    while (time.time() - start_time) < max_duration_sec:
        target_x = rng.uniform(150, vp["width"] - 150)
        target_y = rng.uniform(150, min(vp["height"] - 100, 600))

        simulate_human_mouse_movement(page, target_x, target_y)

        time.sleep(rng.uniform(0.1, 0.4))

        if rng.rand_float() < 0.4:
            scroll_delta = rng.randint(40, 160)
            page.mouse.wheel(0, scroll_delta)
            time.sleep(rng.uniform(0.1, 0.3))
            if rng.rand_float() < 0.3:
                page.mouse.wheel(0, -scroll_delta // 2)


async def async_perform_human_activity(page: AsyncPage, max_duration_sec: float = 2.0):
    """
    Asynchronously simulates organic human browsing behavior.
    """
    vp = page.viewport_size or {"width": 1280, "height": 800}
    start_time = time.time()

    while (time.time() - start_time) < max_duration_sec:
        target_x = rng.uniform(150, vp["width"] - 150)
        target_y = rng.uniform(150, min(vp["height"] - 100, 600))

        await async_simulate_human_mouse_movement(page, target_x, target_y)

        await asyncio.sleep(rng.uniform(0.1, 0.4))

        if rng.rand_float() < 0.4:
            scroll_delta = rng.randint(40, 160)
            await page.mouse.wheel(0, scroll_delta)
            await asyncio.sleep(rng.uniform(0.1, 0.3))
            if rng.rand_float() < 0.3:
                await page.mouse.wheel(0, -scroll_delta // 2)
