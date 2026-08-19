# Quickstart: Foxcape Initial Release

Validation scenarios for manual and live testing. Offline CI uses mocked Camoufox (see `tests/`).

## Prerequisites

```bash
make install
python -m camoufox fetch   # one-time, for live runs only
```

## Scenario 1 — Sync scrape (US1)

```python
from foxcape import Foxcape, FoxcapeConfig

with Foxcape(FoxcapeConfig(headless=True)) as fox:
    result = fox.get("https://example.com", human_delay=False, simulate_mouse=False)
    assert result.title
    assert result.select_one("h1")
print("Scenario 1 OK")
```

## Scenario 2 — Async scrape (US2)

```python
import asyncio
from foxcape import AsyncFoxcape

async def main():
    async with AsyncFoxcape() as fox:
        result = await fox.get("https://example.com", human_delay=False, simulate_mouse=False)
        assert result.title

asyncio.run(main())
print("Scenario 2 OK")
```

## Scenario 3 — Proxy (US3)

```python
from foxcape import Foxcape, FoxcapeConfig, ProxyConfig

cfg = FoxcapeConfig(
    headless=True,
    proxy=ProxyConfig.from_url("http://user:pass@proxy.example:8080"),
)
with Foxcape(cfg) as fox:
    result = fox.get("https://httpbin.org/ip", human_delay=False, simulate_mouse=False)
    assert result.status_code == 200
print("Scenario 3 OK")
```

## Scenario 4 — LLM extraction (US4, offline)

```python
from foxcape import FoxcapeResult

html = """<!DOCTYPE html><html><head><title>T</title></head>
<body><h1>Hi</h1><p>Text<script>bad()</script></p><a href="/x">Link</a></body></html>"""
r = FoxcapeResult.from_html(html, url="https://example.com")
assert "bad()" not in r.get_clean_text()
assert r.extract_links()
assert r.to_markdown()
print("Scenario 4 OK")
```

## Scenario 5 — Profile warmup (US3, live)

```python
from foxcape import ProfileManager, Foxcape

profile = ProfileManager.get_or_create("quickstart-demo")
if not profile.is_warm:
    profile.warmup(steps=1, headless=True)
with Foxcape(profile.to_foxcape_config()) as fox:
    print(fox.get("https://example.com", human_delay=False, simulate_mouse=False).title)
print("Scenario 5 OK")
```

## Scenario 6 — Offline CI (US5)

```bash
make check
```

Expected: ruff, mypy, and **126 offline pytest** cases pass without network or Camoufox fetch.

Optional live validation:

```bash
pytest -m live   # 2 integration tests against example.com
```

## Responsible use

Use Foxcape in compliance with target site terms of service and applicable laws.
