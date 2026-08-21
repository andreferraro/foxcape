"""
Unit and integration tests for Foxcape HTML Cleaner (specs/002-html-cleaner).
All tests are 100% offline and deterministic, using local static fixtures.
"""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from foxcape import AsyncFoxcape, Foxcape, FoxcapeConfig, clean_html
from foxcape.cleaner import CleanerRules, HTMLCleaner

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "cleaner"


def load_fixture(filename: str) -> str:
    fixture_path = FIXTURES_DIR / filename
    return fixture_path.read_text(encoding="utf-8")


# -----------------------------------------------------------------------------
# User Story 1 (P1): Cleaned HTML on demand (MVP)
# -----------------------------------------------------------------------------


def test_clean_html_removes_adsense_and_ad_scripts():
    """T007 [US1]: Verifies AdSense scripts, tags, and iframes are stripped."""
    raw_html = load_fixture("adsense.html")
    cleaned = clean_html(raw_html)

    # Assert ad scripts are stripped
    assert "adsbygoogle.js" not in cleaned
    assert "doubleclick.net" not in cleaned
    assert "googlesyndication.com" not in cleaned

    # Assert ad container / ins elements are stripped
    assert 'class="adsbygoogle"' not in cleaned
    assert 'class="google-auto-placed"' not in cleaned
    assert 'class="ad-container"' not in cleaned
    assert "<iframe" not in cleaned

    # Assert primary article content is completely preserved
    assert "Breaking News: Major Tech Milestone" in cleaned
    assert "primary editorial paragraph" in cleaned
    assert "second paragraph discussing" in cleaned


def test_clean_html_removes_recommendation_widgets():
    """T007 [US1]: Verifies Outbrain, Taboola, and RevContent widgets are stripped."""
    raw_html = load_fixture("taboola_outbrain.html")
    cleaned = clean_html(raw_html)

    # Assert widget scripts are stripped
    assert "widgets.outbrain.com" not in cleaned
    assert "taboola.com" not in cleaned
    assert "revcontent.com" not in cleaned

    # Assert widget elements are stripped
    assert "OUTBRAIN" not in cleaned
    assert "taboola-mid-article" not in cleaned
    assert "taboola-below-article" not in cleaned
    assert "rc-widget" not in cleaned
    assert "revcontent-recommendations" not in cleaned

    # Assert article content is preserved
    assert "Sustainable Software Architecture" in cleaned
    assert "Software sustainability starts with" in cleaned
    assert "adhering to these core engineering tenets" in cleaned


def test_clean_html_removes_cmp_and_cookie_banners():
    """T007 [US1]: Verifies OneTrust, Cookiebot, and generic GDPR banners are removed."""
    raw_html = load_fixture("cmp_consent.html")
    cleaned = clean_html(raw_html)

    # Assert CMP scripts stripped
    assert "cookielaw.org" not in cleaned
    assert "cookiebot.com" not in cleaned

    # Assert CMP banner containers stripped
    assert "onetrust-consent-sdk" not in cleaned
    assert "onetrust-banner-sdk" not in cleaned
    assert "cookie-consent" not in cleaned
    assert "cookie-banner" not in cleaned
    assert "cc-window" not in cleaned

    # Assert main content preserved
    assert "Welcome to the Knowledge Base" in cleaned
    assert "architectural guidelines for resilient" in cleaned


def test_clean_html_graceful_fallback_on_invalid_input():
    """T007 [US1]: Verifies graceful fallback on empty/none/malformed inputs."""
    assert clean_html("") == ""
    assert clean_html(None) is None  # type: ignore[arg-type]

    malformed = "<div><p>Unclosed paragraph and broken tags<ins class='adsbygoogle'>"
    cleaned = clean_html(malformed)
    assert "Unclosed paragraph" in cleaned
    assert "adsbygoogle" not in cleaned


def test_clean_html_subtree_removal_and_nested_elements():
    """CHK009 / CHK015: Verifies nested elements and entire subtrees are cleanly removed."""
    html_with_nested = """
    <html>
        <body>
            <div id="consent-popup" class="cookie-banner">
                <div class="banner-inner">
                    <p>Please accept our cookies.</p>
                    <div class="ad-slot">
                        <iframe src="https://googleads.g.doubleclick.net/ad"></iframe>
                        <span class="nested-ad-text">Click here for sponsor</span>
                    </div>
                </div>
            </div>
            <main>
                <h1>Essential Headline</h1>
                <p>Authentic article paragraph.</p>
            </main>
        </body>
    </html>
    """
    cleaned = clean_html(html_with_nested)

    assert "cookie-banner" not in cleaned
    assert "Please accept our cookies" not in cleaned
    assert "nested-ad-text" not in cleaned
    assert "googleads" not in cleaned
    assert "Essential Headline" in cleaned
    assert "Authentic article paragraph." in cleaned


def test_scraper_sync_clean_html_integration():
    """T008 [US1]: Verifies Foxcape.get() applies clean_html when enabled."""
    raw_html = load_fixture("adsense.html")

    config = FoxcapeConfig(clean_html=True)
    scraper = Foxcape(config=config)

    # Mock page content and url
    mock_page = MagicMock()
    mock_page.content.return_value = raw_html
    mock_page.url = "https://example.com/news"
    scraper._page = mock_page
    scraper.browser = MagicMock()

    with patch("foxcape.scraper.apply_sync_human_cadence"):
        result = scraper.get("https://example.com/news")

    assert "adsbygoogle" not in result.html
    assert "Breaking News" in result.html
    assert result.title == "News Article with Google AdSense"


def test_scraper_sync_fetch_classmethod_integration():
    """T008 [US1]: Verifies Foxcape.fetch() applies clean_html on classmethod invocation."""
    with patch.object(Foxcape, "get") as mock_get:
        mock_result = MagicMock()
        mock_result.html = "Cleaned HTML"
        mock_get.return_value = mock_result

        with patch("foxcape.scraper.Camoufox"):
            res = Foxcape.fetch("https://example.com/test", clean_html=True)
            assert res.html == "Cleaned HTML"
            mock_get.assert_called_once()
            assert mock_get.call_args.kwargs["clean_html"] is True


@pytest.mark.asyncio
async def test_scraper_async_clean_html_integration():
    """T008 [US1]: Verifies AsyncFoxcape.get() applies clean_html when enabled."""
    raw_html = load_fixture("taboola_outbrain.html")

    config = FoxcapeConfig(clean_html=False)
    scraper = AsyncFoxcape(config=config)

    mock_page = MagicMock()

    async def mock_content():
        return raw_html

    async def mock_goto(*args, **kwargs):
        return None

    async def mock_wait_for_selector(*args, **kwargs):
        return None

    mock_page.content = mock_content
    mock_page.goto = mock_goto
    mock_page.wait_for_selector = mock_wait_for_selector
    mock_page.url = "https://example.com/async-article"
    scraper._page = mock_page
    scraper.browser = MagicMock()

    with patch("foxcape.async_scraper.apply_async_human_cadence"):
        # Override clean_html=True on call
        result = await scraper.get("https://example.com/async-article", clean_html=True)

    assert "taboola" not in result.html
    assert "outbrain" not in result.html
    assert "Sustainable Software Architecture" in result.html


@pytest.mark.asyncio
async def test_scraper_async_afetch_classmethod_integration():
    """T008 [US1]: Verifies AsyncFoxcape.afetch() passes clean_html parameter."""
    with patch.object(AsyncFoxcape, "get") as mock_get:

        async def mock_get_impl(*args, **kwargs):
            mock_res = MagicMock()
            mock_res.html = "Cleaned Async HTML"
            return mock_res

        mock_get.side_effect = mock_get_impl
        with patch("foxcape.async_scraper.AsyncCamoufox"):
            res = await AsyncFoxcape.afetch("https://example.com/async", clean_html=True)
            assert res.html == "Cleaned Async HTML"


# -----------------------------------------------------------------------------
# User Story 2 (P1): Unchanged behavior when disabled
# -----------------------------------------------------------------------------


def test_clean_html_disabled_returns_byte_identical_html():
    """T013 [US2]: Verifies raw HTML is returned byte-for-byte unmodified when disabled."""
    raw_html = load_fixture("adsense.html")

    config = FoxcapeConfig(clean_html=False)
    scraper = Foxcape(config=config)

    mock_page = MagicMock()
    mock_page.content.return_value = raw_html
    mock_page.url = "https://example.com/news"
    scraper._page = mock_page
    scraper.browser = MagicMock()

    with patch("foxcape.scraper.apply_sync_human_cadence"):
        result = scraper.get("https://example.com/news")

    # Byte-identical verification
    assert result.html == raw_html
    assert "adsbygoogle" in result.html


def test_legacy_callers_without_clean_html_param():
    """Verifies that legacy callers using legacy config and get signatures work identically."""
    raw_html = (
        "<html><head><title>Legacy Title</title></head>"
        "<body><h1>Legacy Title</h1><div class='ad-slot'>Ad</div></body></html>"
    )

    # Legacy config: no clean_html keyword passed
    legacy_config = FoxcapeConfig(headless=True, simulate_mouse=False)
    assert hasattr(legacy_config, "clean_html")
    assert legacy_config.clean_html is False

    scraper = Foxcape(config=legacy_config)
    mock_page = MagicMock()
    mock_page.content.return_value = raw_html
    mock_page.url = "https://example.com/legacy"
    scraper._page = mock_page
    scraper.browser = MagicMock()

    # Legacy call: positional and keyword args without clean_html
    with patch("foxcape.scraper.apply_sync_human_cadence"):
        result = scraper.get("https://example.com/legacy", wait_selector="h1")

    # Output is 100% untouched and byte-identical
    assert result.html == raw_html
    assert "ad-slot" in result.html
    assert result.title == "Legacy Title"


def test_clean_page_no_false_removals():
    """T013 [US2]: Verifies clean page content is not stripped."""
    raw_html = load_fixture("clean_page.html")
    cleaned = clean_html(raw_html)

    soup = BeautifulSoup(cleaned, "lxml")
    paragraphs = [p.get_text() for p in soup.find_all("p")]
    assert len(paragraphs) == 2
    assert "completely clean HTML page" in paragraphs[0]


# -----------------------------------------------------------------------------
# User Story 3 (P2): Conservative overlay handling
# -----------------------------------------------------------------------------


def test_conservative_overlay_removal_and_modal_preservation():
    """T015 [US3]: Verifies intrusive full-screen fixed overlays are removed while normal modals/headers are preserved."""
    raw_html = load_fixture("overlay.html")
    cleaned = clean_html(raw_html)

    # Assert intrusive fixed fullscreen overlay is removed
    assert "newsletter-overlay" not in cleaned
    assert "floating-interstitial" not in cleaned
    assert "Subscribe to our daily newsletter!" not in cleaned

    # Assert sticky header is preserved
    assert "site-header" in cleaned
    assert "Home" in cleaned

    # Assert normal inline author modal card is preserved (not fixed/high-z)
    assert "author-info-modal" in cleaned
    assert "About the Author" in cleaned
    assert "Experienced systems engineer" in cleaned

    # Assert main content is preserved
    assert "In-Depth Analysis of HTTP Fingerprinting" in cleaned


def test_overlay_negative_cases_prevent_accidental_removal():
    """CHK011 / CHK012: Verifies elements with only modal class or only fixed position (small badge) are NOT removed."""
    html_sample = """
    <html>
        <body>
            <!-- Modal class without fixed position or high z-index -->
            <div class="user-modal-dialog" style="position: relative; margin: 20px;">
                <p>Edit Profile Preferences</p>
            </div>

            <!-- Fixed element with high z-index but small size (back to top button) -->
            <button id="back-to-top" style="position: fixed; bottom: 10px; right: 10px; width: 40px; height: 40px; z-index: 9999;">
                Top
            </button>

            <!-- Real full-screen overlay with fixed + high z + large width -->
            <div id="newsletter-takeover" class="interstitial" style="position: fixed; top: 0; left: 0; width: 90vw; height: 50vh; z-index: 10000;">
                <p>Black Friday 50% Off!</p>
            </div>
        </body>
    </html>
    """
    cleaned = clean_html(html_sample)

    assert "Edit Profile Preferences" in cleaned
    assert "user-modal-dialog" in cleaned
    assert "back-to-top" in cleaned
    assert "newsletter-takeover" not in cleaned
    assert "Black Friday 50% Off!" not in cleaned


# -----------------------------------------------------------------------------
# User Story 4 (P3): Maintainable rules catalog & Engine Options
# -----------------------------------------------------------------------------


def test_custom_rules_extensibility():
    """T017 [US4]: Verifies custom CleanerRules can extend fingerprints dynamically."""
    custom_rules = CleanerRules(
        ad_classes_ids=("custom-sponsor-banner",),
        widget_classes_ids=("partner-recommendations",),
    )

    sample_html = """
    <div>
        <p>Main Article Body</p>
        <div class="custom-sponsor-banner">Sponsor Ad</div>
        <div class="partner-recommendations">Partner Widget</div>
    </div>
    """

    cleaned = clean_html(sample_html, rules=custom_rules)
    assert "custom-sponsor-banner" not in cleaned
    assert "partner-recommendations" not in cleaned
    assert "Main Article Body" in cleaned


def test_cleaner_parser_engine_options_and_performance():
    """SC-005: Verifies html.parser engine option and confirms latency < 5ms."""
    sample_html = load_fixture("adsense.html")

    # Verify html.parser works
    cleaned_html_parser = clean_html(sample_html, parser_engine="html.parser")
    assert "adsbygoogle" not in cleaned_html_parser

    # Verify performance threshold
    start = time.perf_counter()
    for _ in range(10):
        clean_html(sample_html, parser_engine="lxml")
    elapsed = (time.perf_counter() - start) / 10

    # Must take well under 5ms per typical page
    assert elapsed < 0.005, f"Expected < 5ms, got {elapsed * 1000:.2f}ms"


def test_boundary_aware_matching_prevents_false_positives():
    """Verifies that thread-container, download-slot, cookie-recipe and editorial ins are NOT removed."""
    html_with_subnames = """
    <html>
        <body>
            <div id="thread-container" class="thread-container">
                <h2>Discussion Forum</h2>
                <p>Welcome to the main thread.</p>
                <div class="download-slot">
                    <button>Download Report</button>
                </div>
                <div class="cookie-recipe-card">
                    <p>Delicious chocolate chip cookie recipe instructions.</p>
                </div>
                <p>Editorial update: <ins>This is standard editorial inserted text.</ins></p>
            </div>
        </body>
    </html>
    """
    cleaned = clean_html(html_with_subnames)

    assert "thread-container" in cleaned
    assert "Discussion Forum" in cleaned
    assert "download-slot" in cleaned
    assert "Download Report" in cleaned
    assert "cookie-recipe-card" in cleaned
    assert "Delicious chocolate chip cookie recipe instructions." in cleaned
    assert "<ins>" in cleaned
    assert "This is standard editorial inserted text." in cleaned


def test_overlay_css_property_anchoring_excludes_max_width_and_line_height():
    """Verifies max-width and line-height do not trigger width/height overlay heuristics."""
    html_with_max_props = """
    <html>
        <body>
            <!-- Fixed container with max-width and line-height but small actual footprint -->
            <div id="quick-toolbar" style="position: fixed; z-index: 100; max-width: 90vw; line-height: 100%;">
                <button>Action</button>
            </div>
            <!-- Legitimate overlay with actual width: 95vw and height: 60vh -->
            <div id="real-overlay" class="overlay" style="position: fixed; z-index: 100; width: 95vw; height: 60vh;">
                <p>Intrusive Overlay</p>
            </div>
        </body>
    </html>
    """
    cleaned = clean_html(html_with_max_props)
    assert "quick-toolbar" in cleaned
    assert "<button>Action</button>" in cleaned
    assert "real-overlay" not in cleaned
    assert "Intrusive Overlay" not in cleaned


def test_html_cleaner_clean_soup_direct_mutation():
    """Verifies HTMLCleaner.clean_soup directly mutates BeautifulSoup instance."""
    cleaner = HTMLCleaner()
    soup = BeautifulSoup("<div><p>Hello</p><ins class='adsbygoogle'></ins></div>", "lxml")
    cleaned_soup = cleaner.clean_soup(soup)

    assert cleaned_soup.find("ins") is None
    assert cleaned_soup.find("p").get_text() == "Hello"


def test_cleaner_handles_class_as_string_and_exception_fallback():
    """Verifies class as plain string and exception fallback during clean_soup."""
    cleaner = HTMLCleaner()

    # Test class as string
    raw_html = '<div><div class="ad-container">Ad</div><p>Content</p></div>'
    soup = BeautifulSoup(raw_html, "html.parser")
    div_ad = soup.find("div", class_="ad-container")
    div_ad["class"] = "ad-container"  # Force string representation
    cleaner.clean_soup(soup)
    assert "ad-container" not in str(soup)

    # Test exception fallback in clean()
    with patch.object(cleaner, "clean_soup", side_effect=RuntimeError("Simulated DOM crash")):
        res = cleaner.clean("<p>Original Content</p>")
        assert res == "<p>Original Content</p>"

    # Test parser fallback when unknown parser passed
    bad_cleaner = HTMLCleaner(parser_engine="nonexistent_engine")  # type: ignore[arg-type]
    res_fallback = bad_cleaner.clean("<div><ins class='adsbygoogle'></ins><p>Safe</p></div>")
    assert "adsbygoogle" not in res_fallback
    assert "Safe" in res_fallback
