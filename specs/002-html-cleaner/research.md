# Research: Optional HTML Cleaner

**Feature**: Optional HTML Cleaner for Foxcape (`specs/002-html-cleaner/spec.md`)  
**Status**: Complete  
**Date**: 2026-08-21  

---

## 1. DOM Parsing & Engine Strategy

### Decision
Use `BeautifulSoup(html, "lxml")` with fallback to `html.parser` if `lxml` is unavailable or throws a parsing exception.

### Rationale
- **Performance & Native Speed**: `lxml` is already a core runtime dependency of Foxcape. It performs fast C-level tree parsing and tree modification.
- **Robustness**: BeautifulSoup with `lxml` parser gracefully handles malformed HTML, open tags, broken script blocks, and complex nested DOM trees commonly encountered on ad-heavy web pages.
- **Graceful Fallback**: If parsing produces fatal errors, the cleaner returns the original input string untouched, fulfilling requirement `FR-016`.

### Alternatives Considered
- *Regex-only HTML manipulation*: Fast but fragile against nested elements, attribute order, and quotes variations. Rejected.
- *Selectolax / lexbor*: Very fast, but introduces a new third-party dependency, violating Constitution Principle I and `FR-014`.
- *In-browser DOM stripping via JavaScript before `page.content()`*: Modifies page state in Camoufox, risks breaking page scripts/events, cannot be used offline as a standalone utility, and violates Constitution Principle II (Deterministic Offline CI). Rejected.

---

## 2. Fingerprint Rules & Decomposition

### Decision
Separate rule definitions into `src/foxcape/cleaner/rules.py` containing distinct, documented data structures for each category:
1. **Ad Networks (Google AdSense & generic ad containers)**:
   - Tag classes / IDs / attributes: `adsbygoogle`, `google-auto-placed`, `google_ads`, `ad-container`, `ad-slot`, `ad_wrapper`.
   - Script src substrings: `adsbygoogle.js`, `googlesyndication`, `doubleclick.net`.
   - Iframe src substrings: `googleads`, `doubleclick`, `googlesyndication`.
2. **Recommendation Widgets**:
   - Outbrain: class/id matching `outbrain`, `OUTBRAIN`, script src `widgets.outbrain.com`.
   - Taboola: class/id matching `taboola`, `taboola-below-article`, `taboola-mid-article`, script src `trc.taboola.com`, `taboola.com`.
   - RevContent: class/id matching `revcontent`, `rc-widget`, script src `revcontent.com`.
3. **Cookie / LGPD / Consent Banners (CMP)**:
   - Class/id patterns: `cookie`, `cookies`, `consent`, `gdpr`, `privacy`, `cmp`, `cc-window`, `cookie-banner`, `cookie-consent`, `onetrust`.
   - Script src substrings: `onetrust`, `cookiebot`, `quantcast`.
4. **Suspicious Overlay Patterns**:
   - Element style signals: inline `position:\s*(fixed|absolute)` + `z-index:\s*([1-9]\d{2,}|999+)` + viewport width/height patterns (`100vw`, `100%`, `100vh`).
   - Element class/id signals: `modal`, `popup`, `overlay`, `interstitial`, `sticky`, `floating`, `drawer`, `lightbox`, `backdrop`.
   - Heuristic requirement: An overlay is ONLY removed if it matches BOTH a structural style signal (fixed positioning + high z-index) AND an overlay marker (class/id/attribute or full viewport dimensions).

### Rationale
- Decouples maintenance of fingerprints from the execution engine (`FR-012`).
- Maintains an explicit list of high-precision fingerprints rather than generic broad filters that could accidentally strip legitimate article content (`FR-011`).

### Alternatives Considered
- *Full EasyList / AdBlock syntax parser (e.g. adblockparser)*: Introduces large dependencies, complex regex compiling, high latency, and high false-positive rates on content sites. Rejected.
- *LLM / Machine Learning element classifier*: Slow, expensive, non-deterministic, requires network access, violates Constitution Principles II & IV and `FR-015`. Rejected.

---

## 3. Pipeline Order & Execution Flow

### Decision
Execute cleaning in 8 deterministic sequential steps:
1. **Parse**: Build BeautifulSoup tree using configured parser (`lxml`).
2. **Ad Scripts & Iframes**: Strip `<script>` and `<iframe>` tags matching ad/widget network URLs.
3. **Ad Components**: Strip `<ins>`, `<div>`, `<section>` matching AdSense and ad container signatures.
4. **Recommendation Widgets**: Strip Outbrain, Taboola, RevContent widget containers and embed scripts.
5. **Cookie & LGPD CMPs**: Strip CMP containers (OneTrust, Cookiebot, etc.) and consent banners.
6. **Conservative Overlays**: Identify and decompose elements combining fixed positioning, high z-index, and overlay class/id indicators.
7. **Empty Ad Artifacts**: (Optional safety pass) Remove now-empty `<ins class="adsbygoogle">` wrappers.
8. **Serialize**: Output clean HTML string via `.encode().decode()` or `str(soup)`.

### Rationale
- Removing scripts and iframes first reduces tree complexity before scanning container tags.
- Applying specific network rules (AdSense, Taboola, Outbrain) before general heuristics ensures precise removal without accidental cascade effects.

---

## 4. Public API & Configuration Integration

### Decision
1. In `FoxcapeConfig`: add `clean_html: bool = False`.
2. In `Foxcape.get()`, `Foxcape.fetch()`, `AsyncFoxcape.get()`, `AsyncFoxcape.fetch()`: add optional `clean_html: bool | None = None`. If provided, it overrides `self.config.clean_html`.
3. In `foxcape.__all__`: export `clean_html(html: str, parser_engine: str = "lxml") -> str` as a standalone utility.
4. If `clean_html` is evaluated to `False`: the scraper passes `page.content()` directly to `FoxcapeResult.from_html(...)` with zero overhead or tree alterations (byte-identical backward compatibility).

### Rationale
- Fulfills `FR-001`, `FR-013`, `FR-017` and aligns with `src/foxcape/__init__.py` and `FoxcapeResult` architecture.
- 100% backward-compatible.
