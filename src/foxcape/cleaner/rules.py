"""
Catalog of fingerprints, URL substrings, and CSS selectors used by Foxcape HTMLCleaner.
Separated from the cleaning engine for maintainability and extensibility.
"""

import re
from dataclasses import dataclass

# -----------------------------------------------------------------------------
# 1. Ad Networks (Google AdSense, DoubleClick, generic ad slots)
# -----------------------------------------------------------------------------

AD_SCRIPT_URL_PATTERNS: tuple[str, ...] = (
    "adsbygoogle.js",
    "googlesyndication",
    "doubleclick.net",
    "google-analytics.com/ga.js",
    "adservice.google.",
)

AD_IFRAME_URL_PATTERNS: tuple[str, ...] = (
    "googleads",
    "doubleclick",
    "googlesyndication",
    "ad-delivery",
    "adserver",
)

AD_ELEMENT_TAG_NAMES: tuple[str, ...] = ("ins",)

AD_CLASS_ID_PATTERNS: tuple[str, ...] = (
    "adsbygoogle",
    "google-auto-placed",
    "google_ads",
    "google_ad",
    "ad-container",
    "ad_container",
    "ad-slot",
    "ad_slot",
    "ad-wrapper",
    "ad_wrapper",
    "ad-banner",
    "ad_banner",
    "advertisement",
    "dfp-ad",
)

# -----------------------------------------------------------------------------
# 2. Recommendation Widgets (Outbrain, Taboola, RevContent)
# -----------------------------------------------------------------------------

WIDGET_SCRIPT_URL_PATTERNS: tuple[str, ...] = (
    "widgets.outbrain.com",
    "outbrain.js",
    "trc.taboola.com",
    "taboola.com/libtrc",
    "revcontent.com",
)

WIDGET_CLASS_ID_PATTERNS: tuple[str, ...] = (
    "outbrain",
    "OUTBRAIN",
    "taboola",
    "taboola-below-article",
    "taboola-mid-article",
    "taboola-feed",
    "revcontent",
    "rc-widget",
)

# -----------------------------------------------------------------------------
# 3. Cookie / LGPD / GDPR Consent Banners (CMPs)
# -----------------------------------------------------------------------------

CMP_SCRIPT_URL_PATTERNS: tuple[str, ...] = (
    "onetrust",
    "cookielaw.org",
    "cookiebot.com",
    "quantcast",
    "usercentrics",
    "didomi",
    "iubenda",
    "cookie-script.com",
    "termly.io",
)

CMP_CLASS_ID_PATTERNS: tuple[str, ...] = (
    "cookie-banner",
    "cookie-consent",
    "cookie-law",
    "cookie-notice",
    "cookie-popup",
    "cookie-bar",
    "cookies-eu",
    "onetrust-consent-sdk",
    "onetrust-banner-sdk",
    "ot-sdk-container",
    "cookiebot",
    "cc-window",
    "cc-banner",
    "gdpr-banner",
    "gdpr-consent",
    "lgpd-banner",
    "privacy-banner",
    "cmp-container",
    "qc-cmp2-container",
)

# -----------------------------------------------------------------------------
# 4. Overlays & Modals (Conservative Heuristic)
# -----------------------------------------------------------------------------

OVERLAY_SUSPICIOUS_CLASS_ID_PATTERNS: tuple[str, ...] = (
    "modal",
    "popup",
    "overlay",
    "interstitial",
    "sticky",
    "floating",
    "drawer",
    "lightbox",
    "backdrop",
)

# Regular expressions for inline style matching
RE_STYLE_FIXED_OR_ABSOLUTE = re.compile(r"position\s*:\s*(fixed|absolute)", re.IGNORECASE)
RE_STYLE_HIGH_Z_INDEX = re.compile(r"z-index\s*:\s*([1-9]\d{2,}|9999+)", re.IGNORECASE)
RE_STYLE_LARGE_WIDTH = re.compile(r"width\s*:\s*(100|[7-9]\d)(%|vw)", re.IGNORECASE)
RE_STYLE_LARGE_HEIGHT = re.compile(r"height\s*:\s*(100|[3-9]\d)(%|vh)", re.IGNORECASE)
RE_STYLE_LARGE_DIMENSIONS = re.compile(
    r"width\s*:\s*(100|[7-9]\d)(%|vw)|height\s*:\s*(100|[3-9]\d)(%|vh)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CleanerRules:
    """Immutable collection of rules used during HTML cleaning."""

    ad_scripts: tuple[str, ...] = AD_SCRIPT_URL_PATTERNS
    ad_iframes: tuple[str, ...] = AD_IFRAME_URL_PATTERNS
    ad_elements: tuple[str, ...] = AD_ELEMENT_TAG_NAMES
    ad_classes_ids: tuple[str, ...] = AD_CLASS_ID_PATTERNS
    widget_scripts: tuple[str, ...] = WIDGET_SCRIPT_URL_PATTERNS
    widget_classes_ids: tuple[str, ...] = WIDGET_CLASS_ID_PATTERNS
    cmp_scripts: tuple[str, ...] = CMP_SCRIPT_URL_PATTERNS
    cmp_classes_ids: tuple[str, ...] = CMP_CLASS_ID_PATTERNS
    overlay_classes_ids: tuple[str, ...] = OVERLAY_SUSPICIOUS_CLASS_ID_PATTERNS


DEFAULT_RULES = CleanerRules()
