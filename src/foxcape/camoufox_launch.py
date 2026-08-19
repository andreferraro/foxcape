"""Shared Camoufox launch helpers (sync + async scrapers)."""

from typing import Any

from .config import FoxcapeConfig
from .hardware_spoofing import async_inject_hardware_and_webrtc_spoofing, inject_hardware_and_webrtc_spoofing
from .noise_injector import async_inject_fingerprint_noise, inject_fingerprint_noise
from .proxy_pool import ProxyConfig

CAMOUFOX_FETCH_HINT = "Failed to start Camoufox browser. Run `python -m camoufox fetch` to download browser binaries."


def build_camoufox_kwargs(config: FoxcapeConfig) -> dict[str, Any]:
    """Build keyword arguments passed to Camoufox / AsyncCamoufox."""
    kwargs: dict[str, Any] = {
        "headless": config.headless,
        "humanize": config.humanize,
        "geoip": config.geoip,
        "os": config.os,
    }

    if config.fingerprint_preset is not None:
        kwargs["fingerprint_preset"] = config.fingerprint_preset

    if config.disable_coop:
        kwargs["disable_coop"] = True
        if config.i_know_what_im_doing:
            kwargs["i_know_what_im_doing"] = True

    for key, value in (
        ("geoip_db", config.geoip_db),
        ("block_images", config.block_images),
        ("block_webrtc", config.block_webrtc),
        ("block_webgl", config.block_webgl),
        ("enable_cache", config.enable_cache),
        ("window", config.window),
        ("locale", config.locale),
        ("fonts", config.fonts),
    ):
        if value:
            kwargs[key] = value

    if config.proxy:
        kwargs["proxy"] = _proxy_to_playwright(config.proxy)

    if config.user_data_dir:
        kwargs["user_data_dir"] = str(config.user_data_dir)
        kwargs["persistent_context"] = config.persistent_context

    return kwargs


def _proxy_to_playwright(proxy: str | ProxyConfig | dict[str, Any]) -> dict[str, Any]:
    if isinstance(proxy, str):
        return ProxyConfig.from_url(proxy).to_playwright_dict()
    if isinstance(proxy, ProxyConfig):
        return proxy.to_playwright_dict()
    return proxy


def resolve_initial_page(browser: Any) -> Any:
    """Return the first available page from a browser or persistent context."""
    if hasattr(browser, "pages") and len(browser.pages) > 0:
        return browser.pages[0]
    if hasattr(browser, "new_page"):
        return browser.new_page()
    return None


async def async_resolve_initial_page(browser: Any) -> Any:
    """Async variant of resolve_initial_page."""
    if hasattr(browser, "pages") and len(browser.pages) > 0:
        return browser.pages[0]
    if hasattr(browser, "new_page"):
        return await browser.new_page()
    return None


def inject_sync_page_evasions(page: Any, config: FoxcapeConfig) -> None:
    if config.canvas_noise or config.audio_noise:
        inject_fingerprint_noise(page, seed=config.noise_seed)
    if config.hardware_spoofing:
        inject_hardware_and_webrtc_spoofing(page)


async def inject_async_page_evasions(page: Any, config: FoxcapeConfig) -> None:
    if config.canvas_noise or config.audio_noise:
        await async_inject_fingerprint_noise(page, seed=config.noise_seed)
    if config.hardware_spoofing:
        await async_inject_hardware_and_webrtc_spoofing(page)
