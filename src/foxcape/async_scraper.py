import asyncio
from typing import Any

from camoufox.async_api import AsyncCamoufox

from .camoufox_launch import (
    CAMOUFOX_FETCH_HINT,
    async_resolve_initial_page,
    build_camoufox_kwargs,
    inject_async_page_evasions,
)
from .cleaner import clean_html as run_clean_html
from .config import FoxcapeConfig
from .exceptions import BrowserStartupError
from .models import FoxcapeResult
from .scrape_cadence import apply_async_human_cadence
from .turnstile_and_typing import async_human_type, async_solve_turnstile_if_present


class AsyncFoxcape:
    """Asynchronous stealth web scraper powered by Camoufox and Advanced Anti-Bot Evasions."""

    def __init__(self, config: FoxcapeConfig | None = None):
        self.config: FoxcapeConfig = config or FoxcapeConfig()
        self._camoufox_cm: Any = None
        self.browser: Any = None
        self._page: Any = None

    async def __aenter__(self) -> "AsyncFoxcape":
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def start(self) -> None:
        if self.browser is not None:
            return

        camoufox_kwargs = build_camoufox_kwargs(self.config)
        try:
            self._camoufox_cm = AsyncCamoufox(**camoufox_kwargs)
            self.browser = await self._camoufox_cm.__aenter__()
        except Exception as exc:
            self._camoufox_cm = None
            self.browser = None
            raise BrowserStartupError(CAMOUFOX_FETCH_HINT) from exc

        try:
            self._page = await async_resolve_initial_page(self.browser)
            if self._page is not None:
                await inject_async_page_evasions(self._page, self.config)
        except Exception:
            await self.close()
            raise

    async def close(self) -> None:
        if self._page is not None:
            try:
                await self._page.close()
            except Exception:
                pass
            self._page = None
        if self._camoufox_cm is not None:
            try:
                await self._camoufox_cm.__aexit__(None, None, None)
            except Exception:
                pass
            self._camoufox_cm = None
            self.browser = None

    async def get_page(self) -> Any:
        if self.browser is None or self._page is None:
            await self.start()
        if self._page is None:
            raise BrowserStartupError("Failed to initialize async page context.")
        return self._page

    async def aevaluate(self, expression: str, arg: Any | None = None) -> Any:
        page = await self.get_page()
        if arg is not None:
            return await page.evaluate(expression, arg)  # NOSONAR python:S1523
        return await page.evaluate(expression)  # NOSONAR python:S1523

    async def type_human(
        self, selector: str, text: str, typo_probability: float = 0.04, wpm_speed: float = 65.0
    ) -> None:
        page = await self.get_page()
        await async_human_type(page, selector, text, typo_probability=typo_probability, wpm_speed=wpm_speed)

    async def get(
        self,
        url: str,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
        clean_html: bool | None = None,
    ) -> FoxcapeResult:
        if self.browser is None or self._page is None:
            await self.start()

        if self._page is None:
            raise BrowserStartupError("Failed to acquire async page context.")

        target_wait = wait_until or self.config.wait_until
        target_timeout = timeout_ms or self.config.default_timeout_ms

        response = await self._page.goto(url, wait_until=target_wait, timeout=target_timeout)
        status_code = response.status if response else None

        should_solve_turnstile = solve_turnstile if solve_turnstile is not None else self.config.solve_turnstile
        if should_solve_turnstile:
            await async_solve_turnstile_if_present(self._page)

        if wait_selector:
            await self._page.wait_for_selector(wait_selector, timeout=target_timeout)

        should_sim_mouse = simulate_mouse if simulate_mouse is not None else self.config.simulate_mouse
        await apply_async_human_cadence(
            self._page,
            self.config,
            simulate_mouse=should_sim_mouse,
            human_delay=human_delay,
        )

        content = await self._page.content()
        final_url = self._page.url

        should_clean = clean_html if clean_html is not None else self.config.clean_html
        if should_clean:
            content = await asyncio.to_thread(run_clean_html, content, parser_engine=self.config.parser_engine)

        return FoxcapeResult.from_html(
            html=content,
            url=final_url,
            status_code=status_code,
            parser_engine=self.config.parser_engine,
        )

    @classmethod
    async def afetch(
        cls,
        url: str,
        config: FoxcapeConfig | None = None,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
        clean_html: bool | None = None,
    ) -> FoxcapeResult:
        async with cls(config=config) as scraper:
            return await scraper.get(
                url=url,
                wait_selector=wait_selector,
                wait_until=wait_until,
                timeout_ms=timeout_ms,
                simulate_mouse=simulate_mouse,
                solve_turnstile=solve_turnstile,
                human_delay=human_delay,
                clean_html=clean_html,
            )
