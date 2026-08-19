from typing import Any

from camoufox.sync_api import Camoufox

from .camoufox_launch import (
    CAMOUFOX_FETCH_HINT,
    build_camoufox_kwargs,
    inject_sync_page_evasions,
    resolve_initial_page,
)
from .config import FoxcapeConfig
from .exceptions import BrowserStartupError
from .models import FoxcapeResult
from .scrape_cadence import apply_sync_human_cadence
from .turnstile_and_typing import human_type, solve_turnstile_if_present


class Foxcape:
    """Synchronous stealth web scraper powered by Camoufox, BeautifulSoup, and Advanced Anti-Bot Evasions."""

    def __init__(self, config: FoxcapeConfig | None = None):
        self.config: FoxcapeConfig = config or FoxcapeConfig()
        self._camoufox_cm: Any = None
        self.browser: Any = None
        self._page: Any = None

    def __enter__(self) -> "Foxcape":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def start(self) -> None:
        if self.browser is not None:
            return

        camoufox_kwargs = build_camoufox_kwargs(self.config)
        try:
            self._camoufox_cm = Camoufox(**camoufox_kwargs)
            self.browser = self._camoufox_cm.__enter__()
        except Exception as exc:
            self._camoufox_cm = None
            self.browser = None
            raise BrowserStartupError(CAMOUFOX_FETCH_HINT) from exc

        try:
            self._page = resolve_initial_page(self.browser)
            if self._page is not None:
                inject_sync_page_evasions(self._page, self.config)
        except Exception:
            self.close()
            raise

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
            raise BrowserStartupError("Failed to initialize browser page context.")
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
    ) -> FoxcapeResult:
        if self.browser is None or self._page is None:
            self.start()

        if self._page is None:
            raise BrowserStartupError("Failed to acquire page context.")

        target_wait = wait_until or self.config.wait_until
        target_timeout = timeout_ms or self.config.default_timeout_ms

        response = self._page.goto(url, wait_until=target_wait, timeout=target_timeout)
        status_code = response.status if response else None

        should_solve_turnstile = solve_turnstile if solve_turnstile is not None else self.config.solve_turnstile
        if should_solve_turnstile:
            solve_turnstile_if_present(self._page)

        if wait_selector:
            self._page.wait_for_selector(wait_selector, timeout=target_timeout)

        should_sim_mouse = simulate_mouse if simulate_mouse is not None else self.config.simulate_mouse
        apply_sync_human_cadence(
            self._page,
            self.config,
            simulate_mouse=should_sim_mouse,
            human_delay=human_delay,
        )

        content = self._page.content()
        final_url = self._page.url

        return FoxcapeResult.from_html(
            html=content,
            url=final_url,
            status_code=status_code,
            parser_engine=self.config.parser_engine,
        )

    @classmethod
    def fetch(
        cls,
        url: str,
        config: FoxcapeConfig | None = None,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
    ) -> FoxcapeResult:
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
