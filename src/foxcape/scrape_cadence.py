"""Human behavioral cadence applied after navigation."""

import asyncio
import time
from typing import Any

from . import rng
from .cadence import MarkovCadence
from .config import FoxcapeConfig
from .humanizer import async_perform_human_activity, perform_human_activity

_DEFAULT_HUMAN_DELAY_RANGE = (0.5, 2.0)


def _human_delay_bounds(config: FoxcapeConfig) -> tuple[float, float]:
    return config.human_delay_range or _DEFAULT_HUMAN_DELAY_RANGE


def apply_sync_human_cadence(
    page: Any,
    config: FoxcapeConfig,
    *,
    simulate_mouse: bool,
    human_delay: bool,
) -> None:
    if config.use_markov_cadence and (simulate_mouse or human_delay):
        min_delay, max_delay = _human_delay_bounds(config)
        dwell_duration = MarkovCadence.calculate_reading_dwell_time(
            page.content(),
            min_seconds=min_delay,
            max_seconds=max_delay * 1.5,
        )
        if simulate_mouse:
            perform_human_activity(page, max_duration_sec=dwell_duration)
        else:
            time.sleep(dwell_duration)
        return

    if simulate_mouse:
        duration = rng.uniform(*config.human_delay_range) if config.human_delay_range else 1.5
        perform_human_activity(page, max_duration_sec=duration)
        return

    if human_delay and config.human_delay_range:
        min_d, max_d = config.human_delay_range
        time.sleep(rng.uniform(min_d, max_d))


async def apply_async_human_cadence(
    page: Any,
    config: FoxcapeConfig,
    *,
    simulate_mouse: bool,
    human_delay: bool,
) -> None:
    if config.use_markov_cadence and (simulate_mouse or human_delay):
        min_delay, max_delay = _human_delay_bounds(config)
        content_preview = await page.content()
        dwell_duration = MarkovCadence.calculate_reading_dwell_time(
            content_preview,
            min_seconds=min_delay,
            max_seconds=max_delay * 1.5,
        )
        if simulate_mouse:
            await async_perform_human_activity(page, max_duration_sec=dwell_duration)
        else:
            await asyncio.sleep(dwell_duration)
        return

    if simulate_mouse:
        duration = rng.uniform(*config.human_delay_range) if config.human_delay_range else 1.5
        await async_perform_human_activity(page, max_duration_sec=duration)
        return

    if human_delay and config.human_delay_range:
        min_d, max_d = config.human_delay_range
        await asyncio.sleep(rng.uniform(min_d, max_d))
