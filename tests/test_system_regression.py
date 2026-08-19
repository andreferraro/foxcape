"""System and regression tests after v0.1.0 refactors (camoufox_launch, scrape_cadence, profiles)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from foxcape import (
    AsyncFoxcape,
    BrowserStartupError,
    Foxcape,
    FoxcapeConfig,
    FoxcapeResult,
    ProfileManager,
    ProxyPoolManager,
)
from foxcape.camoufox_launch import build_camoufox_kwargs
from foxcape.profiles import BrowserProfile
from foxcape.scrape_cadence import apply_async_human_cadence, apply_sync_human_cadence
from foxcape.turnstile_and_typing import (
    _normalize_wpm_speed,
    _wait_turnstile_resolution_async,
    async_solve_turnstile_if_present,
    human_type,
    solve_turnstile_if_present,
)

REALISTIC_HTML = """
<!DOCTYPE html>
<html><head><title>Shop</title></head>
<body>
  <nav><a href="/catalog">Catalog</a></nav>
  <main>
    <h1>Featured</h1>
    <p>Buy now<script>track()</script></p>
    <a href="https://shop.example/item/1">Item 1</a>
  </main>
</body></html>
"""


class TestPostRefactorSystemFlows:
    """End-to-end mocked flows through refactored launch + cadence modules."""

    def test_sync_full_feature_scrape_uses_launch_and_cadence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[str] = []
        page = MagicMock()
        page.goto.return_value = MagicMock(status=201)
        page.content.return_value = REALISTIC_HTML
        page.url = "https://shop.example/"
        browser = MagicMock(pages=[page])
        cm = MagicMock()
        cm.__enter__ = MagicMock(return_value=browser)
        cm.__exit__ = MagicMock(return_value=False)
        monkeypatch.setattr("foxcape.scraper.Camoufox", MagicMock(return_value=cm))
        monkeypatch.setattr(
            "foxcape.camoufox_launch.inject_fingerprint_noise",
            lambda p, seed=None: calls.append("noise"),
        )
        monkeypatch.setattr(
            "foxcape.camoufox_launch.inject_hardware_and_webrtc_spoofing",
            lambda p: calls.append("hardware"),
        )
        monkeypatch.setattr(
            "foxcape.scraper.solve_turnstile_if_present",
            lambda p: calls.append("turnstile") or True,
        )
        monkeypatch.setattr(
            "foxcape.scraper.apply_sync_human_cadence",
            lambda *args, **kwargs: calls.append("cadence"),
        )

        cfg = FoxcapeConfig(
            headless=True,
            canvas_noise=True,
            hardware_spoofing=True,
            solve_turnstile=True,
            use_markov_cadence=True,
        )
        with Foxcape(cfg) as fox:
            result = fox.get("https://shop.example/", human_delay=True)

        assert result.title == "Shop"
        assert result.status_code == 201
        assert result.select_one("h1") is not None
        assert "noise" in calls
        assert "hardware" in calls
        assert "turnstile" in calls
        assert "cadence" in calls

    @pytest.mark.asyncio
    async def test_async_full_feature_scrape_uses_launch_and_cadence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        calls: list[str] = []
        page = MagicMock()
        page.goto = AsyncMock(return_value=MagicMock(status=202))
        page.content = AsyncMock(return_value=REALISTIC_HTML)
        page.url = "https://shop.example/async"
        browser = MagicMock(pages=[page])
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=browser)
        cm.__aexit__ = AsyncMock(return_value=False)
        monkeypatch.setattr("foxcape.async_scraper.AsyncCamoufox", MagicMock(return_value=cm))

        async def mark_noise(p, seed=None) -> None:
            calls.append("noise")

        async def mark_hw(p) -> None:
            calls.append("hardware")

        async def mark_ts(p) -> None:
            calls.append("turnstile")
            return True

        async def mark_cadence(*args, **kwargs) -> None:
            calls.append("cadence")

        monkeypatch.setattr("foxcape.camoufox_launch.async_inject_fingerprint_noise", mark_noise)
        monkeypatch.setattr("foxcape.camoufox_launch.async_inject_hardware_and_webrtc_spoofing", mark_hw)
        monkeypatch.setattr("foxcape.async_scraper.async_solve_turnstile_if_present", mark_ts)
        monkeypatch.setattr("foxcape.async_scraper.apply_async_human_cadence", mark_cadence)

        cfg = FoxcapeConfig(headless=True, canvas_noise=True, hardware_spoofing=True, solve_turnstile=True)
        async with AsyncFoxcape(cfg) as fox:
            result = await fox.get("https://shop.example/", human_delay=True)

        assert result.title == "Shop"
        assert result.status_code == 202
        assert set(calls) >= {"noise", "hardware", "turnstile", "cadence"}

    def test_profile_proxy_config_reaches_camoufox_kwargs(self, tmp_path) -> None:
        profile = ProfileManager.get_or_create("prod", profiles_dir=tmp_path)
        pool = ProxyPoolManager()
        pool.add_proxy("http://user:pass@proxy.test:8888")
        proxy = pool.get_proxy(session_id="sess-a")
        cfg = profile.to_foxcape_config(FoxcapeConfig(headless=True, proxy=proxy, user_data_dir=profile.profile_dir))
        kwargs = build_camoufox_kwargs(cfg)
        assert kwargs["proxy"]["server"] == "http://proxy.test:8888"
        assert kwargs["user_data_dir"] == str(profile.profile_dir)
        assert kwargs["persistent_context"] is True


class TestPostRefactorRegressionFixes:
    """Guards for CodeRabbit/rebase fixes — must not regress."""

    def test_build_camoufox_kwargs_i_know_without_disable_coop(self) -> None:
        kwargs = build_camoufox_kwargs(
            FoxcapeConfig(disable_coop=False, i_know_what_im_doing=True),
        )
        assert "disable_coop" not in kwargs
        assert kwargs["i_know_what_im_doing"] is True

    def test_normalize_wpm_speed_rejects_non_finite_and_non_positive(self) -> None:
        assert _normalize_wpm_speed(0.0) == 65.0
        assert _normalize_wpm_speed(-10.0) == 65.0
        assert _normalize_wpm_speed(float("nan")) == 65.0
        assert _normalize_wpm_speed(float("inf")) == 65.0
        assert _normalize_wpm_speed(80.0) == 80.0

    def test_profile_metadata_coerces_non_list_visited_domains(self, tmp_path) -> None:
        profile_dir = tmp_path / "bad-domains"
        profile_dir.mkdir()
        (profile_dir / "profile_metadata.json").write_text(
            json.dumps({"name": "bad-domains", "visited_domains": "not-a-list"}),
            encoding="utf-8",
        )
        profile = BrowserProfile("bad-domains", tmp_path)
        assert profile.metadata["visited_domains"] == []
        profile._record_warmup_visit("https://x.example/y")
        assert profile.metadata["visited_domains"] == ["x.example"]

    @pytest.mark.asyncio
    async def test_async_get_raises_when_page_missing_after_start(self, monkeypatch: pytest.MonkeyPatch) -> None:
        browser = MagicMock()
        browser.pages = []
        browser.new_page = AsyncMock(return_value=None)
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=browser)
        monkeypatch.setattr("foxcape.async_scraper.AsyncCamoufox", MagicMock(return_value=cm))

        fox = AsyncFoxcape(FoxcapeConfig(headless=True, canvas_noise=False, hardware_spoofing=False))
        with pytest.raises(BrowserStartupError, match="Failed to acquire async page context"):
            await fox.get("https://example.com", human_delay=False)

    @pytest.mark.asyncio
    async def test_async_scrape_cadence_simple_mouse_without_markov(self) -> None:
        page = MagicMock()
        cfg = FoxcapeConfig(use_markov_cadence=False, human_delay_range=(0.4, 0.8))
        with patch("foxcape.scrape_cadence.rng.uniform", return_value=0.6):
            with patch("foxcape.scrape_cadence.async_perform_human_activity", new_callable=AsyncMock) as mock_activity:
                await apply_async_human_cadence(page, cfg, simulate_mouse=True, human_delay=False)
        mock_activity.assert_awaited_once_with(page, max_duration_sec=0.6)

    def test_sync_scrape_cadence_human_delay_only_with_none_range_skips(self) -> None:
        page = MagicMock()
        cfg = FoxcapeConfig(use_markov_cadence=False, human_delay_range=None)
        with patch("foxcape.scrape_cadence.time.sleep") as mock_sleep:
            with patch("foxcape.scrape_cadence.perform_human_activity") as mock_activity:
                apply_sync_human_cadence(page, cfg, simulate_mouse=False, human_delay=True)
        mock_sleep.assert_not_called()
        mock_activity.assert_not_called()


class TestTurnstileAndTypingDepth:
    """Deeper behavioral coverage for turnstile solver and human typing."""

    def test_human_type_uppercase_typo_uses_upper_neighbor(self) -> None:
        page = MagicMock()
        page.locator.return_value.first = MagicMock()
        kb = MagicMock()
        page.keyboard = kb
        with patch("foxcape.turnstile_and_typing.time.sleep"):
            with patch("foxcape.turnstile_and_typing.rng.uniform", return_value=0.05):
                with patch("foxcape.turnstile_and_typing.rng.rand_float", return_value=0.01):
                    with patch("foxcape.turnstile_and_typing.rng.choice", return_value="s"):
                        with patch("foxcape.turnstile_and_typing.rng.lognormvariate", return_value=0.05):
                            human_type(page, "#f", "A", typo_probability=1.0)
        kb.press.assert_any_call("S")

    def test_solve_turnstile_returns_false_when_no_bounding_box(self) -> None:
        page = MagicMock()
        iframe = MagicMock()
        iframe.count.return_value = 1
        iframe.is_visible.return_value = True
        iframe.bounding_box.return_value = None
        page.locator.return_value = iframe
        assert solve_turnstile_if_present(page) is False

    def test_solve_turnstile_returns_false_on_wait_timeout(self) -> None:
        page = MagicMock()
        page.viewport_size = {"width": 1280, "height": 800}
        page.mouse = MagicMock()
        iframe = MagicMock()
        iframe.count.return_value = 1
        iframe.is_visible.return_value = True
        iframe.bounding_box.return_value = {"x": 0, "y": 0, "width": 300, "height": 65}
        token_loc = MagicMock()
        token_loc.count.return_value = 0
        token_loc.first.input_value.return_value = ""

        def locator_side_effect(sel: str):
            if "cf-turnstile-response" in sel:
                return token_loc
            return iframe

        page.locator.side_effect = locator_side_effect
        with patch("foxcape.turnstile_and_typing.generate_windmouse_path", return_value=[(1.0, 1.0, 0.0)]):
            with patch("foxcape.turnstile_and_typing.time.sleep"):
                with patch("foxcape.turnstile_and_typing.rng.uniform", return_value=100.0):
                    with patch("foxcape.turnstile_and_typing._is_turnstile_resolved_sync", return_value=False):
                        assert solve_turnstile_if_present(page, timeout_sec=0.05) is False

    @pytest.mark.asyncio
    async def test_async_turnstile_wait_continues_after_transient_errors(self) -> None:
        page = MagicMock()
        iframe = MagicMock()

        async def resolve_side_effect(*args, **kwargs):
            resolve_side_effect.calls += 1
            if resolve_side_effect.calls == 1:
                raise RuntimeError("detached")
            return True

        resolve_side_effect.calls = 0

        with patch(
            "foxcape.turnstile_and_typing._is_turnstile_resolved_async",
            side_effect=resolve_side_effect,
        ):
            with patch("foxcape.turnstile_and_typing.asyncio.sleep", new_callable=AsyncMock):
                assert await _wait_turnstile_resolution_async(page, iframe, timeout_sec=1.0) is True

    @pytest.mark.asyncio
    async def test_async_solve_turnstile_returns_false_without_iframe(self) -> None:
        page = MagicMock()
        loc = MagicMock()
        loc.count = AsyncMock(return_value=0)
        page.locator.return_value = loc
        assert await async_solve_turnstile_if_present(page) is False


class TestFunctionalExtractionPipeline:
    """Offline functional validation of LLM-friendly extraction (spec US-4)."""

    def test_result_extraction_pipeline_on_realistic_html(self) -> None:
        result = FoxcapeResult.from_html(REALISTIC_HTML, url="https://shop.example/catalog")
        text = result.get_clean_text()
        md = result.to_markdown()
        links = result.extract_links()

        assert "Featured" in text
        assert "track()" not in text
        assert "# Featured" in md or "Featured" in md
        assert any(link.get("href", "").endswith("/item/1") or "item/1" in link.get("href", "") for link in links)

    @pytest.mark.asyncio
    async def test_humanizer_async_mouse_applies_path_delays(self) -> None:
        from foxcape.humanizer import async_simulate_human_mouse_movement

        page = MagicMock()
        page.viewport_size = {"width": 1280, "height": 800}
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        sleeps: list[float] = []

        async def capture_sleep(delay: float) -> None:
            sleeps.append(delay)

        with patch("foxcape.humanizer.generate_windmouse_path", return_value=[(10.0, 10.0, 0.05), (20.0, 20.0, 0.0)]):
            with patch("foxcape.humanizer.asyncio.sleep", side_effect=capture_sleep):
                await async_simulate_human_mouse_movement(page, 100.0, 200.0)

        assert page.mouse.move.await_count == 2
        assert sleeps == [0.05]
