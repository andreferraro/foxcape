from types import SimpleNamespace

import pytest

from foxcape import AsyncFoxcape, Foxcape, FoxcapeConfig
from foxcape.exceptions import BrowserStartupError


class FakePage:
    url = "https://example.com/final"

    def __init__(self) -> None:
        self.closed = False
        self.goto_calls: list[tuple[str, str, int]] = []
        self.waited: list[tuple[str, int]] = []
        self.evaluated: list[tuple[str, object | None]] = []
        self.typed: list[tuple[str, str]] = []

    def goto(self, url: str, wait_until: str, timeout: int) -> SimpleNamespace:
        self.goto_calls.append((url, wait_until, timeout))
        return SimpleNamespace(status=202)

    def wait_for_selector(self, selector: str, timeout: int) -> None:
        self.waited.append((selector, timeout))

    def content(self) -> str:
        return "<html><title>Fake</title><h1>Ok</h1></html>"

    def evaluate(self, expression: str, arg: object | None = None) -> tuple[str, object | None]:
        self.evaluated.append((expression, arg))
        return expression, arg

    def close(self) -> None:
        self.closed = True


class FakeBrowser:
    def __init__(self, page: FakePage | None = None) -> None:
        self.pages = [] if page is None else [page]
        self.created = FakePage()

    def new_page(self) -> FakePage:
        return self.created


class FakeCamoufox:
    kwargs: dict | None = None
    browser: FakeBrowser | None = None
    exited = False

    def __init__(self, **kwargs) -> None:
        type(self).kwargs = kwargs
        self.browser = type(self).browser or FakeBrowser(FakePage())

    def __enter__(self) -> FakeBrowser:
        return self.browser

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        type(self).exited = True


class AsyncFakePage(FakePage):
    async def goto(self, url: str, wait_until: str, timeout: int) -> SimpleNamespace:
        self.goto_calls.append((url, wait_until, timeout))
        return SimpleNamespace(status=203)

    async def wait_for_selector(self, selector: str, timeout: int) -> None:
        self.waited.append((selector, timeout))

    async def content(self) -> str:
        return "<html><title>Async Fake</title><h1>Ok</h1></html>"

    async def evaluate(self, expression: str, arg: object | None = None) -> tuple[str, object | None]:
        self.evaluated.append((expression, arg))
        return expression, arg

    async def close(self) -> None:
        self.closed = True


class AsyncFakeBrowser:
    def __init__(self, page: AsyncFakePage | None = None) -> None:
        self.pages = [] if page is None else [page]
        self.created = AsyncFakePage()

    async def new_page(self) -> AsyncFakePage:
        return self.created


class AsyncFakeCamoufox:
    kwargs: dict | None = None
    browser: AsyncFakeBrowser | None = None
    exited = False

    def __init__(self, **kwargs) -> None:
        type(self).kwargs = kwargs
        self.browser = type(self).browser or AsyncFakeBrowser(AsyncFakePage())

    async def __aenter__(self) -> AsyncFakeBrowser:
        return self.browser

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        type(self).exited = True


def rich_config(tmp_path) -> FoxcapeConfig:
    return FoxcapeConfig(
        headless=True,
        humanize=False,
        geoip=False,
        os=["windows", "linux"],
        fingerprint_preset={"screen": "desktop"},
        disable_coop=True,
        i_know_what_im_doing=True,
        geoip_db="geo.mmdb",
        block_images=True,
        block_webrtc=True,
        block_webgl=True,
        window=(1280, 720),
        locale=["en-US"],
        fonts=["Arial"],
        proxy="http://user:pass@example.com:9000",
        user_data_dir=tmp_path / "profile",
        persistent_context=True,
        noise_seed=99,
        use_markov_cadence=True,
        human_delay_range=(0.1, 0.2),
    )


def test_sync_scraper_lifecycle_and_get(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    calls: list[str] = []
    page = FakePage()
    monkeypatch.setattr(FakeCamoufox, "browser", FakeBrowser(page))
    monkeypatch.setattr(FakeCamoufox, "exited", False)

    monkeypatch.setattr("foxcape.scraper.Camoufox", FakeCamoufox)
    monkeypatch.setattr("foxcape.scraper.inject_fingerprint_noise", lambda p, seed=None: calls.append(f"noise:{seed}"))
    monkeypatch.setattr("foxcape.scraper.inject_hardware_and_webrtc_spoofing", lambda p: calls.append("hardware"))
    monkeypatch.setattr("foxcape.scraper.solve_turnstile_if_present", lambda p: calls.append("turnstile"))
    monkeypatch.setattr("foxcape.scraper.perform_human_activity", lambda p, max_duration_sec: calls.append("activity"))
    monkeypatch.setattr("foxcape.scraper.MarkovCadence.calculate_reading_dwell_time", lambda *args, **kwargs: 0.1)
    monkeypatch.setattr("foxcape.scraper.time.sleep", lambda _: calls.append("sleep"))

    scraper = Foxcape(rich_config(tmp_path))
    assert scraper.evaluate("1 + 1", {"x": 1}) == ("1 + 1", {"x": 1})
    result = scraper.get("https://example.com", wait_selector="h1")

    assert result.title == "Fake"
    assert result.status_code == 202
    assert page.goto_calls == [("https://example.com", "domcontentloaded", 30000)]
    assert page.waited == [("h1", 30000)]
    assert {"noise:99", "hardware", "turnstile", "activity"}.issubset(set(calls))
    assert FakeCamoufox.kwargs["proxy"]["server"] == "http://example.com:9000"

    scraper.close()
    assert page.closed is True
    assert FakeCamoufox.exited is True


def test_sync_scraper_uses_new_page_and_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(FakeCamoufox, "browser", FakeBrowser(None))
    monkeypatch.setattr(FakeCamoufox, "exited", False)
    monkeypatch.setattr("foxcape.scraper.Camoufox", FakeCamoufox)
    monkeypatch.setattr("foxcape.scraper.inject_fingerprint_noise", lambda p, seed=None: None)
    monkeypatch.setattr("foxcape.scraper.inject_hardware_and_webrtc_spoofing", lambda p: None)
    monkeypatch.setattr("foxcape.scraper.time.sleep", lambda _: None)

    scraper = Foxcape(FoxcapeConfig(simulate_mouse=False, solve_turnstile=False, use_markov_cadence=False))
    scraper.start()
    assert scraper.page is FakeCamoufox.browser.created

    fetched = Foxcape.fetch(
        "https://example.com",
        config=FoxcapeConfig(simulate_mouse=False, solve_turnstile=False, use_markov_cadence=False),
        human_delay=False,
    )
    assert fetched.title == "Fake"


def test_sync_scraper_raises_when_no_page(monkeypatch: pytest.MonkeyPatch) -> None:
    class EmptyBrowser:
        pages: list = []

    class EmptyCamoufox(FakeCamoufox):
        def __enter__(self):
            return EmptyBrowser()

    monkeypatch.setattr("foxcape.scraper.Camoufox", EmptyCamoufox)
    scraper = Foxcape(FoxcapeConfig(canvas_noise=False, hardware_spoofing=False))

    with pytest.raises(BrowserStartupError):
        _ = scraper.page


async def test_async_scraper_lifecycle_and_get(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    calls: list[str] = []
    page = AsyncFakePage()
    monkeypatch.setattr(AsyncFakeCamoufox, "browser", AsyncFakeBrowser(page))
    monkeypatch.setattr(AsyncFakeCamoufox, "exited", False)

    async def async_noise(p, seed=None) -> None:
        calls.append(f"noise:{seed}")

    async def async_hardware(p) -> None:
        calls.append("hardware")

    async def async_turnstile(p) -> None:
        calls.append("turnstile")

    async def async_activity(p, max_duration_sec) -> None:
        calls.append("activity")

    async def async_sleep(delay: float) -> None:
        calls.append("sleep")

    monkeypatch.setattr("foxcape.async_scraper.AsyncCamoufox", AsyncFakeCamoufox)
    monkeypatch.setattr("foxcape.async_scraper.async_inject_fingerprint_noise", async_noise)
    monkeypatch.setattr("foxcape.async_scraper.async_inject_hardware_and_webrtc_spoofing", async_hardware)
    monkeypatch.setattr("foxcape.async_scraper.async_solve_turnstile_if_present", async_turnstile)
    monkeypatch.setattr("foxcape.async_scraper.async_perform_human_activity", async_activity)
    monkeypatch.setattr("foxcape.async_scraper.MarkovCadence.calculate_reading_dwell_time", lambda *args, **kwargs: 0.1)
    monkeypatch.setattr("foxcape.async_scraper.asyncio.sleep", async_sleep)

    scraper = AsyncFoxcape(rich_config(tmp_path))
    assert await scraper.aevaluate("window.x", 1) == ("window.x", 1)
    result = await scraper.get("https://example.com", wait_selector="h1")

    assert result.title == "Async Fake"
    assert result.status_code == 203
    assert page.waited == [("h1", 30000)]
    assert {"noise:99", "hardware", "turnstile", "activity"}.issubset(set(calls))

    await scraper.close()
    assert page.closed is True
    assert AsyncFakeCamoufox.exited is True


async def test_async_scraper_new_page_fetch_and_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(AsyncFakeCamoufox, "browser", AsyncFakeBrowser(None))
    monkeypatch.setattr(AsyncFakeCamoufox, "exited", False)

    async def noop(*args, **kwargs) -> None:
        return None

    monkeypatch.setattr("foxcape.async_scraper.AsyncCamoufox", AsyncFakeCamoufox)
    monkeypatch.setattr("foxcape.async_scraper.async_inject_fingerprint_noise", noop)
    monkeypatch.setattr("foxcape.async_scraper.async_inject_hardware_and_webrtc_spoofing", noop)

    scraper = AsyncFoxcape(FoxcapeConfig(simulate_mouse=False, solve_turnstile=False, use_markov_cadence=False))
    await scraper.start()
    assert await scraper.get_page() is AsyncFakeCamoufox.browser.created

    fetched = await AsyncFoxcape.afetch(
        "https://example.com",
        config=FoxcapeConfig(simulate_mouse=False, solve_turnstile=False, use_markov_cadence=False),
        human_delay=False,
    )
    assert fetched.title == "Async Fake"

    class EmptyBrowser:
        pages: list = []

    class EmptyAsyncCamoufox(AsyncFakeCamoufox):
        async def __aenter__(self):
            return EmptyBrowser()

    monkeypatch.setattr("foxcape.async_scraper.AsyncCamoufox", EmptyAsyncCamoufox)
    broken = AsyncFoxcape(FoxcapeConfig(canvas_noise=False, hardware_spoofing=False))
    with pytest.raises(BrowserStartupError):
        await broken.get_page()
