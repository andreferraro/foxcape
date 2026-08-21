"""
HTMLCleaner engine for Foxcape.
Removes advertising, recommendation widgets, CMP cookie banners, and intrusive overlays.
"""

import logging
import re
from typing import Literal

from bs4 import BeautifulSoup, Tag

from .rules import (
    DEFAULT_RULES,
    RE_STYLE_FIXED_OR_ABSOLUTE,
    RE_STYLE_HIGH_Z_INDEX,
    RE_STYLE_LARGE_HEIGHT,
    RE_STYLE_LARGE_WIDTH,
    CleanerRules,
)

logger = logging.getLogger(__name__)


def _extract_tag_identifiers(tag: Tag) -> list[str]:
    candidates: list[str] = []
    tag_id = tag.get("id")
    if isinstance(tag_id, str):
        candidates.append(tag_id.lower())

    tag_classes = tag.get("class")
    if isinstance(tag_classes, list):
        for cls_name in tag_classes:
            if isinstance(cls_name, str):
                candidates.append(cls_name.lower())
    elif isinstance(tag_classes, str):
        candidates.extend(tag_classes.lower().split())

    return candidates


def _item_matches_pattern(item: str, pat: str) -> bool:
    pat_lower = pat.lower()
    if "-" in pat_lower or "_" in pat_lower:
        return item == pat_lower or bool(re.search(r"(?:^|[\s_])" + re.escape(pat_lower) + r"(?:$|[\s_])", item))
    return item == pat_lower or bool(re.search(r"(?:^|[\s])" + re.escape(pat_lower) + r"(?:$|[\s])", item))


class HTMLCleaner:
    """Modular DOM cleaning engine applying rule-based sanitization passes."""

    def __init__(
        self,
        rules: CleanerRules | None = None,
        parser_engine: Literal["lxml", "html.parser"] = "lxml",
    ) -> None:
        self.rules = rules or DEFAULT_RULES
        self.parser_engine = parser_engine

    def clean(self, html: str) -> str:
        """Executes the full 8-step cleaning pipeline on an HTML string.

        If parsing fails or produces an unexpected error, safely returns the original input.
        """
        if not html or not isinstance(html, str):
            return html

        try:
            try:
                soup = BeautifulSoup(html, self.parser_engine)
            except Exception:
                # Fallback to standard html.parser if lxml fails
                soup = BeautifulSoup(html, "html.parser")

            self.clean_soup(soup)
            return str(soup)
        except Exception as exc:
            logger.warning(
                "HTMLCleaner encountered an error during cleaning; returning original input. Error: %s",
                exc,
            )
            return html

    def clean_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Applies sanitization rules in-place to an existing BeautifulSoup tree."""
        self._remove_scripts(soup)
        self._remove_iframes(soup)
        self._remove_ad_components(soup)
        self._remove_widgets(soup)
        self._remove_cmp_banners(soup)
        self._remove_conservative_overlays(soup)
        return soup

    def _matches_any_pattern(self, text: str, patterns: tuple[str, ...]) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        return any(pattern.lower() in text_lower for pattern in patterns)

    def _tag_matches_class_or_id(self, tag: Tag, patterns: tuple[str, ...]) -> bool:
        candidates = _extract_tag_identifiers(tag)
        return any(_item_matches_pattern(item, pat) for item in candidates for pat in patterns)

    def _remove_scripts(self, soup: BeautifulSoup) -> None:
        """Stage 2: Remove known advertising, widget, and CMP scripts."""
        script_patterns = self.rules.ad_scripts + self.rules.widget_scripts + self.rules.cmp_scripts
        for script in soup.find_all("script"):
            src = script.get("src", "")
            script_id = script.get("id", "")
            if (isinstance(src, str) and self._matches_any_pattern(src, script_patterns)) or (
                isinstance(script_id, str) and self._matches_any_pattern(script_id, script_patterns)
            ):
                script.decompose()

    def _remove_iframes(self, soup: BeautifulSoup) -> None:
        """Stage 3: Remove known advertising iframes."""
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src", "")
            if isinstance(src, str) and self._matches_any_pattern(src, self.rules.ad_iframes):
                iframe.decompose()

    def _remove_ad_components(self, soup: BeautifulSoup) -> None:
        """Stage 4: Remove AdSense tags and ad containers."""
        for el in soup.find_all(True):
            if el.decomposed:
                continue

            # Check <ins> or configured ad element tags
            if el.name in self.rules.ad_elements:
                has_ad_class = self._tag_matches_class_or_id(el, self.rules.ad_classes_ids)
                has_ad_attrs = bool(el.get("data-ad-client") or el.get("data-ad-slot") or el.get("data-ad-format"))
                if has_ad_class or has_ad_attrs:
                    el.decompose()
            elif self._tag_matches_class_or_id(el, self.rules.ad_classes_ids):
                el.decompose()

    def _remove_widgets(self, soup: BeautifulSoup) -> None:
        """Stage 5: Remove recommendation widgets (Outbrain, Taboola, RevContent)."""
        for el in soup.find_all(True):
            if el.decomposed:
                continue
            if self._tag_matches_class_or_id(el, self.rules.widget_classes_ids):
                el.decompose()

    def _remove_cmp_banners(self, soup: BeautifulSoup) -> None:
        """Stage 6: Remove CMP and cookie/LGPD consent banners."""
        for el in soup.find_all(True):
            if el.decomposed:
                continue
            if self._tag_matches_class_or_id(el, self.rules.cmp_classes_ids):
                el.decompose()

    def _remove_conservative_overlays(self, soup: BeautifulSoup) -> None:
        """Stage 7: Conservatively identify and remove intrusive full-screen fixed overlays.

        Requires:
        1. Structural style signals: inline position (fixed or absolute) AND high z-index.
        AND
        2. Viewport coverage:
           - Both large width and large height (fullscreen takeover), OR
           - Large width combined with an overlay/modal/interstitial marker.
        """
        for el in soup.find_all(True):
            if el.decomposed or el.name in ("html", "head", "body", "main", "article"):
                continue

            style = el.get("style")
            if not style or not isinstance(style, str):
                continue

            has_fixed_pos = bool(RE_STYLE_FIXED_OR_ABSOLUTE.search(style))
            has_high_z = bool(RE_STYLE_HIGH_Z_INDEX.search(style))
            has_large_width = bool(RE_STYLE_LARGE_WIDTH.search(style))
            has_large_height = bool(RE_STYLE_LARGE_HEIGHT.search(style))
            has_overlay_marker = self._tag_matches_class_or_id(el, self.rules.overlay_classes_ids)

            is_fullscreen_takeover = has_large_width and has_large_height
            is_marked_large_overlay = has_large_width and has_overlay_marker

            if has_fixed_pos and has_high_z and (is_fullscreen_takeover or is_marked_large_overlay):
                el.decompose()


def clean_html(
    html: str,
    parser_engine: Literal["lxml", "html.parser"] = "lxml",
    rules: CleanerRules | None = None,
) -> str:
    """Standalone utility function to clean rendered HTML.

    Args:
        html: Raw HTML string to sanitize.
        parser_engine: Parser backend to use ("lxml" or "html.parser").
        rules: Optional custom CleanerRules instance.

    Returns:
        Cleaned, serialized HTML string.
    """
    cleaner = HTMLCleaner(rules=rules, parser_engine=parser_engine)
    return cleaner.clean(html)
