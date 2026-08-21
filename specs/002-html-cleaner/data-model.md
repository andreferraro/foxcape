# Data Model & Domain Architecture: HTML Cleaner

**Feature**: Optional HTML Cleaner for Foxcape (`specs/002-html-cleaner/spec.md`)  
**Status**: Complete  
**Date**: 2026-08-21  

---

## 1. Domain Entities & Taxonomy

```
+-------------------------------------------------------------+
|                       Foxcape Pipeline                      |
+-------------------------------------------------------------+
                               |
                        clean_html=True
                               |
                               v
+-------------------------------------------------------------+
|                         HTMLCleaner                         |
|  - parser_engine: Literal["lxml", "html.parser"]           |
+-------------------------------------------------------------+
                               |
         +---------------------+---------------------+
         |                     |                     |
         v                     v                     v
+-----------------+   +-----------------+   +-----------------+
|   RuleRegistry  |   |  ElementFilter  |   | OverlayDetector |
|  - ad_rules     |   |  - decompose()  |   | - check_style() |
|  - widget_rules |   |  - prune_tree() |   | - check_class() |
|  - cmp_rules    |   +-----------------+   +-----------------+
|  - overlay_rules|
+-----------------+
```

---

## 2. Entities & Dataclasses

### 2.1 `CleanerRuleSet`
A container holding compile-ready fingerprint collections for the cleaner pipeline.

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `ad_script_patterns` | `tuple[str, ...]` | URL substrings identifying ad network script tags. |
| `ad_iframe_patterns` | `tuple[str, ...]` | URL substrings identifying ad network iframe tags. |
| `ad_class_patterns` | `tuple[str, ...]` | CSS class & ID substrings for ad components (`adsbygoogle`, etc.). |
| `widget_patterns` | `tuple[str, ...]` | Fingerprints for Outbrain, Taboola, RevContent widgets & scripts. |
| `cmp_patterns` | `tuple[str, ...]` | CSS class, ID, and script substrings for cookie/LGPD banners & CMPs. |
| `overlay_class_patterns` | `tuple[str, ...]` | Class & ID substrings representing modals, overlays, popups. |
| `overlay_style_signals` | `tuple[str, ...]` | CSS inline style properties representing fixed/high-z overlays. |

### 2.2 `HTMLCleaner`
The primary engine class that encapsulates the cleaning pipeline.

| Method | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `clean(html)` | `html: str` | `str` | Parses, executes the 8-step pipeline, and returns the cleaned serialized HTML string. |
| `clean_soup(soup)` | `soup: BeautifulSoup` | `BeautifulSoup` | Mutates the provided BeautifulSoup tree directly in-memory, removing unwanted nodes. |

---

## 3. Configuration & Options Model

### `FoxcapeConfig` additions

```python
@dataclass
class FoxcapeConfig:
    # ... existing settings ...
    clean_html: bool = False
    parser_engine: Literal["lxml", "html.parser"] = "lxml"
```

### Call-level Override Matrix

| `FoxcapeConfig.clean_html` | Method call argument `clean_html` | Effective Behavior |
| :---: | :---: | :--- |
| `False` | `None` (omitted) | **Cleaner disabled** (raw HTML returned, 0 overhead). |
| `False` | `True` | **Cleaner enabled** (HTML cleaned via `clean_html`). |
| `True` | `None` (omitted) | **Cleaner enabled** (HTML cleaned via `clean_html`). |
| `True` | `False` | **Cleaner disabled** (raw HTML returned). |
