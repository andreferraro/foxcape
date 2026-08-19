"""
StealthScraper: State-of-the-Art Undetectable Web Scraping Library
Powered by Camoufox, BeautifulSoup, WindMouse Kinematics, and Anti-Bot Evasions.
"""

from .async_scraper import AsyncStealthScraper
from .cadence import MarkovCadence
from .config import ScraperConfig
from .hardware_spoofing import (
    async_inject_hardware_and_webrtc_spoofing,
    get_deep_hardware_and_webrtc_spoof_script,
    inject_hardware_and_webrtc_spoofing,
)
from .humanizer import (
    async_perform_human_activity,
    async_simulate_human_mouse_movement,
    generate_windmouse_path,
    perform_human_activity,
    simulate_human_mouse_movement,
)
from .models import ScrapeResult
from .noise_injector import (
    async_inject_fingerprint_noise,
    get_canvas_and_audio_noise_script,
    inject_fingerprint_noise,
)
from .parsers import build_soup, dom_to_markdown_summary, extract_clean_text, extract_links_from_soup
from .profiles import BrowserProfile, ProfileManager
from .proxy_pool import ProxyConfig, ProxyPoolManager
from .scraper import StealthScraper
from .turnstile_and_typing import (
    async_human_type,
    async_solve_turnstile_if_present,
    human_type,
    solve_turnstile_if_present,
)

__version__ = "1.0.0"

__all__ = [
    "ScraperConfig",
    "ScrapeResult",
    "StealthScraper",
    "AsyncStealthScraper",
    "generate_windmouse_path",
    "simulate_human_mouse_movement",
    "async_simulate_human_mouse_movement",
    "perform_human_activity",
    "async_perform_human_activity",
    "get_canvas_and_audio_noise_script",
    "inject_fingerprint_noise",
    "async_inject_fingerprint_noise",
    "get_deep_hardware_and_webrtc_spoof_script",
    "inject_hardware_and_webrtc_spoofing",
    "async_inject_hardware_and_webrtc_spoofing",
    "human_type",
    "async_human_type",
    "solve_turnstile_if_present",
    "async_solve_turnstile_if_present",
    "MarkovCadence",
    "BrowserProfile",
    "ProfileManager",
    "ProxyConfig",
    "ProxyPoolManager",
    "build_soup",
    "extract_clean_text",
    "extract_links_from_soup",
    "dom_to_markdown_summary",
]
