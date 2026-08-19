from typing import Any

from .config import FoxcapeConfig
from .proxy_pool import ProxyConfig


def build_camoufox_kwargs(config: FoxcapeConfig) -> dict[str, Any]:
    """Build Camoufox launch options from Foxcape configuration."""
    camoufox_kwargs: dict[str, Any] = {
        "headless": config.headless,
        "humanize": config.humanize,
        "geoip": config.geoip,
        "os": config.os,
    }
    if config.fingerprint_preset is not None:
        camoufox_kwargs["fingerprint_preset"] = config.fingerprint_preset
    if config.disable_coop:
        camoufox_kwargs["disable_coop"] = True
        if config.i_know_what_im_doing:
            camoufox_kwargs["i_know_what_im_doing"] = True
    if config.geoip_db:
        camoufox_kwargs["geoip_db"] = config.geoip_db
    if config.block_images:
        camoufox_kwargs["block_images"] = config.block_images
    if config.block_webrtc:
        camoufox_kwargs["block_webrtc"] = config.block_webrtc
    if config.block_webgl:
        camoufox_kwargs["block_webgl"] = config.block_webgl
    if config.enable_cache:
        camoufox_kwargs["enable_cache"] = config.enable_cache
    if config.window:
        camoufox_kwargs["window"] = config.window
    if config.locale:
        camoufox_kwargs["locale"] = config.locale
    if config.fonts:
        camoufox_kwargs["fonts"] = config.fonts
    if config.proxy:
        if isinstance(config.proxy, str):
            camoufox_kwargs["proxy"] = ProxyConfig.from_url(config.proxy).to_playwright_dict()
        elif isinstance(config.proxy, ProxyConfig):
            camoufox_kwargs["proxy"] = config.proxy.to_playwright_dict()
        else:
            camoufox_kwargs["proxy"] = config.proxy
    if config.user_data_dir:
        camoufox_kwargs["user_data_dir"] = str(config.user_data_dir)
        camoufox_kwargs["persistent_context"] = config.persistent_context

    return camoufox_kwargs
