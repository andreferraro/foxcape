# Implementation Plan: Optional HTML Cleaner

**Branch**: `002-html-cleaner` | **Date**: 2026-08-21 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-html-cleaner/spec.md`

---

## Summary

Add an optional HTML cleaning module (`foxcape.cleaner`) to Foxcape. When `clean_html=True` is set on `FoxcapeConfig` or passed as a per-call override, the rendered HTML is parsed via `BeautifulSoup` (with `lxml`) and processed through an 8-stage rule pipeline to remove Google AdSense, external recommendation widgets (Outbrain, Taboola, RevContent), CMP/cookie consent banners (OneTrust, Cookiebot, etc.), and intrusive overlays. When disabled or omitted, Foxcape behaves with zero modifications (byte-identical backward compatibility). A standalone utility function `clean_html(html)` is exported directly in `foxcape.__all__` for offline usage.

---

## Technical Context

**Language/Version**: Python >= 3.10
**Primary Dependencies**: `beautifulsoup4`, `lxml`, `camoufox[geoip]` (existing runtime dependencies, NO new dependencies added)
**Storage**: N/A (in-memory DOM transformation)
**Testing**: `pytest`, `pytest-cov`, `pytest-asyncio`, `hypothesis`
**Target Platform**: Linux, macOS, Windows
**Project Type**: Python Library
**Performance Goals**: < 5ms processing time per typical web page DOM
**Constraints**: Zero new runtime dependencies, 100% deterministic offline test execution (`pytest -m "not live"`), zero overhead when disabled
**Scale/Scope**: Modular rules catalog in `src/foxcape/cleaner/rules.py` and engine in `src/foxcape/cleaner/cleaner.py`

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status | Notes |
| :--- | :--- | :---: | :--- |
| **I. Public Library Boundary** | Zero coupling to consumer apps. Runtime deps: `camoufox[geoip]`, `beautifulsoup4`, `lxml` only. | **PASS** | Uses existing `beautifulsoup4` and `lxml`. Zero new dependencies. |
| **II. Deterministic Offline CI** | `pytest -m "not live"` blocks merge. No network, no camoufox fetch in default CI. | **PASS** | Cleaner tests use offline HTML string fixtures without browser launches. |
| **III. Camoufox-Only Engine** | Playwright not in public API (`__all__`). Internal use only. | **PASS** | Cleaner operates purely on serialized HTML / BeautifulSoup trees. |
| **IV. Ponytail / YAGNI** | Simplest solution, no speculative abstractions, standard patterns. | **PASS** | Clean rule-based tag decompose passes; no ML, no heavy filter-lists parser. |
| **V. Stable Public API** | `__all__` defines public surface. | **PASS** | `clean_html` exported in `foxcape.__all__`; `FoxcapeConfig.clean_html: bool = False` backward-compatible. |

---

## Project Structure

### Documentation (this feature)

```text
specs/002-html-cleaner/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cleaner-api.md   # Cleaner API interface contracts
├── checklists/          # Validation checklists
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/foxcape/
├── __init__.py           # Export clean_html in __all__
├── config.py             # Add clean_html: bool = False to FoxcapeConfig
├── scraper.py            # Add clean_html override to get() and fetch()
├── async_scraper.py      # Add clean_html override to async get() and fetch()
└── cleaner/              # [NEW] HTML Cleaner module
    ├── __init__.py       # Expose HTMLCleaner and clean_html
    ├── rules.py          # Fingerprints & selectors for Ads, Widgets, CMPs, Overlays
    └── cleaner.py        # Pipeline implementation (HTMLCleaner)

tests/
├── test_cleaner.py       # [NEW] Unit & fixture tests for cleaner rules & pipeline
└── fixtures/cleaner/     # [NEW] Offline HTML sample fixtures
    ├── adsense_page.html
    ├── taboola_outbrain_page.html
    ├── consent_banner_page.html
    ├── overlay_page.html
    └── clean_article_page.html
```

**Structure Decision**: Single modular subpackage `src/foxcape/cleaner/` inside existing `src/foxcape/` layout.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| :--- | :--- | :--- |
| *None* | N/A (Fully compliant with all principles) | N/A |
