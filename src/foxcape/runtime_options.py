from typing import Any

from .config import FoxcapeConfig
from .proxy_pool import ProxyConfig

OPTIONAL_FLAG_FIELDS = (
    "geoip_db",
    "block_images",
    "block_webrtc",
    "block_webgl",
    "enable_cache",
    "window",
    "locale",
    "fonts",
)


def normalize_proxy(proxy: dict[str, str] | ProxyConfig | str) -> dict[str, str]:
    if isinstance(proxy, str):
        return ProxyConfig.from_url(proxy).to_playwright_dict()
    if isinstance(proxy, ProxyConfig):
        return proxy.to_playwright_dict()
    return proxy


def add_present_options(camoufox_kwargs: dict[str, Any], config: FoxcapeConfig) -> None:
    for field in OPTIONAL_FLAG_FIELDS:
        value = getattr(config, field)
        if value:
            camoufox_kwargs[field] = value


def add_persistent_context_options(camoufox_kwargs: dict[str, Any], config: FoxcapeConfig) -> None:
    if config.user_data_dir:
        camoufox_kwargs["user_data_dir"] = str(config.user_data_dir)
        camoufox_kwargs["persistent_context"] = config.persistent_context


def add_advanced_options(camoufox_kwargs: dict[str, Any], config: FoxcapeConfig) -> None:
    if config.fingerprint_preset is not None:
        camoufox_kwargs["fingerprint_preset"] = config.fingerprint_preset
    if config.disable_coop:
        camoufox_kwargs["disable_coop"] = True
        if config.i_know_what_im_doing:
            camoufox_kwargs["i_know_what_im_doing"] = True
    add_present_options(camoufox_kwargs, config)
    if config.proxy:
        camoufox_kwargs["proxy"] = normalize_proxy(config.proxy)
    add_persistent_context_options(camoufox_kwargs, config)


def build_camoufox_kwargs(config: FoxcapeConfig) -> dict[str, Any]:
    """Build Camoufox launch options from Foxcape configuration."""
    camoufox_kwargs: dict[str, Any] = {
        "headless": config.headless,
        "humanize": config.humanize,
        "geoip": config.geoip,
        "os": config.os,
    }
    add_advanced_options(camoufox_kwargs, config)

    return camoufox_kwargs
