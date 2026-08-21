from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .proxy_pool import ProxyConfig


@dataclass
class FoxcapeConfig:
    """Configuration settings for Foxcape (Camoufox stealth scraper)."""

    headless: bool | Literal["virtual"] = False
    humanize: bool | float = True
    simulate_mouse: bool = True
    canvas_noise: bool = True
    audio_noise: bool = True
    hardware_spoofing: bool = True
    solve_turnstile: bool = True
    use_markov_cadence: bool = True
    noise_seed: int | None = None
    fingerprint_preset: bool | dict[str, Any] | None = None
    geoip: bool | str = True
    geoip_db: str | None = None
    os: str | list[str] | None = "windows"
    disable_coop: bool = False
    i_know_what_im_doing: bool = False
    block_images: bool = False
    block_webrtc: bool = False
    block_webgl: bool = False
    enable_cache: bool = False
    user_data_dir: str | Path | None = None
    persistent_context: bool = False
    proxy: dict[str, str] | ProxyConfig | str | None = None
    window: tuple[int, int] | None = None
    locale: str | list[str] | None = None
    fonts: list[str] | None = None

    # Navigation & Timing
    wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = "domcontentloaded"
    default_timeout_ms: int = 30000
    human_delay_range: tuple[float, float] = (0.5, 2.0)
    parser_engine: Literal["lxml", "html.parser"] = "lxml"
    clean_html: bool = False
