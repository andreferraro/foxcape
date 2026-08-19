"""Fingerprint noise and hardware spoofing init scripts."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from foxcape.hardware_spoofing import (
    async_inject_hardware_and_webrtc_spoofing,
    get_deep_hardware_and_webrtc_spoof_script,
    inject_hardware_and_webrtc_spoofing,
)
from foxcape.noise_injector import (
    async_inject_fingerprint_noise,
    get_canvas_and_audio_noise_script,
    inject_fingerprint_noise,
)


def test_noise_script_contains_seed_when_provided() -> None:
    script = get_canvas_and_audio_noise_script(seed=424242)
    assert "424242" in script
    assert "HTMLCanvasElement" in script
    assert "AudioBuffer" in script


def test_noise_script_generates_random_seed_when_none() -> None:
    script = get_canvas_and_audio_noise_script(seed=None)
    assert "const SEED =" in script


def test_inject_fingerprint_noise_sync() -> None:
    page = MagicMock()
    inject_fingerprint_noise(page, seed=12345)
    page.add_init_script.assert_called_once()
    assert "12345" in page.add_init_script.call_args[0][0]


@pytest.mark.asyncio
async def test_inject_fingerprint_noise_async() -> None:
    page = MagicMock()
    page.add_init_script = AsyncMock()
    await async_inject_fingerprint_noise(page, seed=999)
    page.add_init_script.assert_awaited_once()
    assert "999" in page.add_init_script.call_args[0][0]


def test_hardware_spoof_script_covers_key_apis() -> None:
    script = get_deep_hardware_and_webrtc_spoof_script()
    assert "hardwareConcurrency" in script
    assert "deviceMemory" in script
    assert "enumerateDevices" in script
    assert "getBattery" in script
    assert "[native code]" in script


def test_inject_hardware_spoofing_sync() -> None:
    page = MagicMock()
    inject_hardware_and_webrtc_spoofing(page)
    page.add_init_script.assert_called_once()
    assert "hardwareConcurrency" in page.add_init_script.call_args[0][0]


@pytest.mark.asyncio
async def test_inject_hardware_spoofing_async() -> None:
    page = MagicMock()
    page.add_init_script = AsyncMock()
    await async_inject_hardware_and_webrtc_spoofing(page)
    page.add_init_script.assert_awaited_once()
