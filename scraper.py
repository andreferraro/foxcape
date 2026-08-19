import random
import time
from typing import Any

from camoufox.sync_api import Camoufox

from .cadence import MarkovCadence
from .config import ScraperConfig
from .hardware_spoofing import inject_hardware_and_webrtc_spoofing
from .humanizer import perform_human_activity
from .models import ScrapeResult
from .noise_injector import inject_fingerprint_noise
from .proxy_pool import ProxyConfig
from .turnstile_and_typing import human_type, solve_turnstile_if_present


class StealthScraper:
    """Synchronous stealth web scraper powered by Camoufox, BeautifulSoup, and Advanced Anti-Bot Evasions."""

    def __init__(self, config: ScraperConfig | None = None):
        self.config: ScraperConfig = config or ScraperConfig()
        self._camoufox_cm: Any = None
        self.browser: Any = None
        self._page: Any = None

    def __enter__(self) -> "StealthScraper":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def start(self) -> None:
        if self.browser is None:
            camoufox_kwargs: dict[str, Any] = {
                "headless": self.config.headless,
                "humanize": self.config.humanize,
                "geoip": self.config.geoip,
                "os": self.config.os,
            }
            if self.config.fingerprint_preset is not None:
                camoufox_kwargs["fingerprint_preset"] = self.config.fingerprint_preset
            if self.config.disable_coop:
                camoufox_kwargs["disable_coop"] = True
                if self.config.i_know_what_im_doing:
                    camoufox_kwargs["i_know_what_im_doing"] = True
            if self.config.geoip_db:
                camoufox_kwargs["geoip_db"] = self.config.geoip_db
            if self.config.block_images:
                camoufox_kwargs["block_images"] = self.config.block_images
            if self.config.block_webrtc:
                camoufox_kwargs["block_webrtc"] = self.config.block_webrtc
            if self.config.block_webgl:
                camoufox_kwargs["block_webgl"] = self.config.block_webgl
            if self.config.window:
                camoufox_kwargs["window"] = self.config.window
            if self.config.locale:
                camoufox_kwargs["locale"] = self.config.locale
            if self.config.fonts:
                camoufox_kwargs["fonts"] = self.config.fonts
            if self.config.proxy:
                if isinstance(self.config.proxy, str):
                    camoufox_kwargs["proxy"] = ProxyConfig.from_url(self.config.proxy).to_playwright_dict()
                elif isinstance(self.config.proxy, ProxyConfig):
                    camoufox_kwargs["proxy"] = self.config.proxy.to_playwright_dict()
                else:
                    camoufox_kwargs["proxy"] = self.config.proxy
            if self.config.user_data_dir:
                camoufox_kwargs["user_data_dir"] = str(self.config.user_data_dir)
                camoufox_kwargs["persistent_context"] = self.config.persistent_context

            self._camoufox_cm = Camoufox(**camoufox_kwargs)
            self.browser = self._camoufox_cm.__enter__()

            # Handle both Browser and BrowserContext (persistent context)
            if hasattr(self.browser, "pages") and len(self.browser.pages) > 0:
                self._page = self.browser.pages[0]
            elif hasattr(self.browser, "new_page"):
                self._page = self.browser.new_page()

            # 1. Inject Canvas and Web Audio per-session noise
            if self._page is not None and (self.config.canvas_noise or self.config.audio_noise):
                inject_fingerprint_noise(self._page, seed=self.config.noise_seed)

            # 2. Inject deep hardware and WebRTC consistency spoofing
            if self._page is not None and self.config.hardware_spoofing:
                inject_hardware_and_webrtc_spoofing(self._page)

    def close(self) -> None:
        if self._page is not None:
            try:
                self._page.close()
            except Exception:
                pass
            self._page = None
        if self._camoufox_cm is not None:
            try:
                self._camoufox_cm.__exit__(None, None, None)
            except Exception:
                pass
            self._camoufox_cm = None
            self.browser = None

    @property
    def page(self) -> Any:
        """Returns the active Camoufox page instance, starting the browser if needed."""
        if self.browser is None or self._page is None:
            self.start()
        if self._page is None:
            raise RuntimeError("Failed to initialize browser page context.")
        return self._page

    def evaluate(self, expression: str, arg: Any | None = None) -> Any:
        """Evaluates JavaScript expression in the active Camoufox page context."""
        if arg is not None:
            return self.page.evaluate(expression, arg)
        return self.page.evaluate(expression)

    def type_human(self, selector: str, text: str, typo_probability: float = 0.04, wpm_speed: float = 65.0) -> None:
        """Types into an input with authentic human biometrics."""
        if self.browser is None or self._page is None:
            self.start()
        if self._page is not None:
            human_type(self._page, selector, text, typo_probability=typo_probability, wpm_speed=wpm_speed)

    def get(
        self,
        url: str,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
    ) -> ScrapeResult:
        if self.browser is None or self._page is None:
            self.start()

        if self._page is None:
            raise RuntimeError("Failed to acquire page context.")

        target_wait = wait_until or self.config.wait_until
        target_timeout = timeout_ms or self.config.default_timeout_ms

        response = self._page.goto(url, wait_until=target_wait, timeout=target_timeout)
        status_code = response.status if response else None

        # Check and resolve Cloudflare Turnstile if present
        should_solve_turnstile = solve_turnstile if solve_turnstile is not None else self.config.solve_turnstile
        if should_solve_turnstile:
            solve_turnstile_if_present(self._page)

        if wait_selector:
            self._page.wait_for_selector(wait_selector, timeout=target_timeout)

        # Advanced Human Behavioral Cadence (Markov Chain + WindMouse)
        should_sim_mouse = simulate_mouse if simulate_mouse is not None else self.config.simulate_mouse

        if self.config.use_markov_cadence and (should_sim_mouse or human_delay):
            content_preview = self._page.content()
            dwell_duration = MarkovCadence.calculate_reading_dwell_time(
                content_preview,
                min_seconds=self.config.human_delay_range[0],
                max_seconds=self.config.human_delay_range[1] * 1.5,
            )
            if should_sim_mouse:
                perform_human_activity(self._page, max_duration_sec=dwell_duration)
            else:
                time.sleep(dwell_duration)
        elif should_sim_mouse:
            duration = random.uniform(*self.config.human_delay_range) if self.config.human_delay_range else 1.5
            perform_human_activity(self._page, max_duration_sec=duration)
        elif human_delay and self.config.human_delay_range:
            min_d, max_d = self.config.human_delay_range
            time.sleep(random.uniform(min_d, max_d))

        content = self._page.content()
        final_url = self._page.url

        return ScrapeResult.from_html(
            html=content,
            url=final_url,
            status_code=status_code,
            parser_engine=self.config.parser_engine,
        )

    @classmethod
    def fetch(
        cls,
        url: str,
        config: ScraperConfig | None = None,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
    ) -> ScrapeResult:
        with cls(config=config) as scraper:
            return scraper.get(
                url=url,
                wait_selector=wait_selector,
                wait_until=wait_until,
                timeout_ms=timeout_ms,
                simulate_mouse=simulate_mouse,
                solve_turnstile=solve_turnstile,
                human_delay=human_delay,
            )
