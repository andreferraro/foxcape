"""Camoufox launch helpers: kwargs building, page resolution, evasion injection."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foxcape.camoufox_launch import (
    async_resolve_initial_page,
    build_camoufox_kwargs,
    inject_async_page_evasions,
    inject_sync_page_evasions,
    resolve_initial_page,
)
from foxcape.config import FoxcapeConfig
from foxcape.proxy_pool import ProxyConfig


def test_build_camoufox_kwargs_minimal_defaults() -> None:
    kwargs = build_camoufox_kwargs(FoxcapeConfig())
    assert kwargs["headless"] is False
    assert kwargs["humanize"] is True
    assert kwargs["geoip"] is True
    assert "proxy" not in kwargs
    assert "user_data_dir" not in kwargs


def test_build_camoufox_kwargs_full_options(tmp_path: Path) -> None:
    cfg = FoxcapeConfig(
        headless=True,
        fingerprint_preset={"screen": {"width": 1920}},
        disable_coop=True,
        i_know_what_im_doing=True,
        block_images=True,
        block_webrtc=True,
        block_webgl=True,
        window=(1280, 720),
        locale="pt-BR",
        fonts=["Arial"],
        geoip_db="/tmp/GeoLite2.mmdb",
        proxy=ProxyConfig(server="http://proxy:8080", username="u", password="p"),
        user_data_dir=tmp_path / "profile",
        persistent_context=True,
    )
    kwargs = build_camoufox_kwargs(cfg)
    assert kwargs["fingerprint_preset"] == {"screen": {"width": 1920}}
    assert kwargs["disable_coop"] is True
    assert kwargs["i_know_what_im_doing"] is True
    assert kwargs["block_images"] is True
    assert kwargs["proxy"]["server"] == "http://proxy:8080"
    assert kwargs["user_data_dir"] == str(tmp_path / "profile")
    assert kwargs["persistent_context"] is True


def test_build_camoufox_kwargs_proxy_from_string() -> None:
    kwargs = build_camoufox_kwargs(FoxcapeConfig(proxy="http://user:pass@proxy:3128"))
    assert kwargs["proxy"]["username"] == "user"


def test_build_camoufox_kwargs_proxy_dict_passthrough() -> None:
    proxy_dict = {"server": "http://custom:8080"}
    kwargs = build_camoufox_kwargs(FoxcapeConfig(proxy=proxy_dict))
    assert kwargs["proxy"] == proxy_dict


def test_resolve_initial_page_uses_existing_page() -> None:
    page = MagicMock()
    browser = MagicMock(pages=[page])
    assert resolve_initial_page(browser) is page


def test_resolve_initial_page_creates_new_when_empty() -> None:
    new_page = MagicMock()
    browser = MagicMock(pages=[])
    browser.new_page = MagicMock(return_value=new_page)
    assert resolve_initial_page(browser) is new_page


def test_resolve_initial_page_returns_none_when_no_api() -> None:
    assert resolve_initial_page(object()) is None


@pytest.mark.asyncio
async def test_async_resolve_initial_page_creates_new() -> None:
    new_page = MagicMock()
    browser = MagicMock(pages=[])
    browser.new_page = AsyncMock(return_value=new_page)
    assert await async_resolve_initial_page(browser) is new_page


def test_inject_sync_page_evasions_all_flags() -> None:
    page = MagicMock()
    cfg = FoxcapeConfig(canvas_noise=True, audio_noise=True, hardware_spoofing=True, noise_seed=777)
    with patch("foxcape.camoufox_launch.inject_fingerprint_noise") as mock_noise:
        with patch("foxcape.camoufox_launch.inject_hardware_and_webrtc_spoofing") as mock_hw:
            inject_sync_page_evasions(page, cfg)
    mock_noise.assert_called_once_with(page, seed=777)
    mock_hw.assert_called_once_with(page)


@pytest.mark.asyncio
async def test_inject_async_page_evasions_all_flags() -> None:
    page = MagicMock()
    cfg = FoxcapeConfig(canvas_noise=True, hardware_spoofing=True)
    with patch("foxcape.camoufox_launch.async_inject_fingerprint_noise", new_callable=AsyncMock) as mock_noise:
        with patch(
            "foxcape.camoufox_launch.async_inject_hardware_and_webrtc_spoofing", new_callable=AsyncMock
        ) as mock_hw:
            await inject_async_page_evasions(page, cfg)
    mock_noise.assert_awaited_once()
    mock_hw.assert_awaited_once()
