# Quickstart: Testing & Validating the HTML Cleaner

**Feature**: Optional HTML Cleaner (`specs/002-html-cleaner/spec.md`)  
**Status**: Ready  
**Date**: 2026-08-21  

---

## 1. Standalone Offline Usage

Clean an HTML file or string directly without starting Camoufox or Playwright:

```python
from foxcape import clean_html

raw_html = """
<html>
  <body>
    <h1>Article Title</h1>
    <ins class="adsbygoogle" style="display:block"></ins>
    <div id="onetrust-banner-sdk">Cookie banner</div>
    <div class="outbrain-widget">Sponsored Content</div>
    <div style="position: fixed; z-index: 9999; width: 100vw; height: 100vh;" class="modal-overlay">Overlay</div>
    <p>Legitimate news article content.</p>
  </body>
</html>
"""

cleaned = clean_html(raw_html)
assert "adsbygoogle" not in cleaned
assert "onetrust-banner-sdk" not in cleaned
assert "outbrain-widget" not in cleaned
assert "Legitimate news article content." in cleaned
```

---

## 2. Scraping with `clean_html=True`

### Via Config (all requests cleaned by default)
```python
from foxcape import Foxcape, FoxcapeConfig

config = FoxcapeConfig(clean_html=True)
with Foxcape(config) as scraper:
    result = scraper.get("https://news-site.example.com")
    print(result.html)  # Returned HTML is already stripped of ads and banners
```

### Via Per-call Override
```python
from foxcape import Foxcape

with Foxcape() as scraper:
    # Uncleaned by default:
    raw_result = scraper.get("https://news-site.example.com")
    
    # Cleaned on demand:
    clean_result = scraper.get("https://news-site.example.com", clean_html=True)
```

---

## 3. Running Deterministic Offline Verification

All cleaner tests run 100% offline using `pytest`:

```bash
pytest tests/test_cleaner.py -v
```

Run entire test suite offline to verify no regressions:
```bash
pytest -m "not live"
```
