# Foxcape

Undetectable Python web scraping library — [Camoufox](https://camoufox.com/) stealth browser, BeautifulSoup parsing, and layered anti-bot evasions in one `pip install`.

**Python** `>=3.10` · **License** MIT · **Import** `from foxcape import Foxcape, FoxcapeConfig, FoxcapeResult`

---

## What Foxcape does

Foxcape is a library for developers who need to fetch web pages that block headless browsers, datacenter IPs, or scripted traffic. It wraps a patched Firefox (Camoufox), applies fingerprint and behavior evasions automatically, and returns parsed HTML you can query with CSS selectors, clean text, markdown, or link lists.

| Layer | What you get |
|-------|----------------|
| **Browser** | Camoufox — anti-fingerprint Firefox with GeoIP-aware profiles |
| **Evasions** | Canvas/audio noise, hardware & WebRTC spoofing, optional Turnstile solver |
| **Behavior** | WindMouse paths, Markov reading cadence, biometric typing, organic scrolling |
| **Networking** | HTTP/SOCKS proxies with round-robin, random, or sticky sessions |
| **Persistence** | Disk-backed browser profiles with optional warmup sequences |
| **Parsing** | `FoxcapeResult` — CSS selectors, clean text, markdown, structured links |

Sync and async APIs share the same config and behavior. Low-level helpers (mouse paths, noise scripts, parsers) are exported for custom Playwright/Camoufox integrations.

---

## Features

### Scraping (`Foxcape` / `AsyncFoxcape`)

- Context-manager lifecycle — browser starts on enter, cleans up on exit
- `get()` / `aget()` — navigate, optional wait for selector, return `FoxcapeResult`
- `fetch()` / `afetch()` — one-shot scrape without manual lifecycle
- `evaluate()` / `aevaluate()` — run JavaScript in the live page
- `type_human()` — fill forms with human-like keystroke timing and typos
- Per-request overrides: `wait_until`, `timeout_ms`, `simulate_mouse`, `solve_turnstile`, `human_delay`

### Anti-fingerprint evasions (on by default)

Injected before page scripts run via Camoufox init scripts:

| Evasion | Module | Effect |
|---------|--------|--------|
| Canvas & audio noise | `noise_injector` | Sub-pixel canvas jitter and Web Audio frequency noise — unique per-session hash without breaking rendering |
| Hardware spoofing | `hardware_spoofing` | Consistent `hardwareConcurrency`, `deviceMemory`, Permissions API, Network Information, Battery, mediaDevices, PDF viewer |
| WebRTC hardening | `hardware_spoofing` | Reduces internal IP leaks through peer connection hooks |
| Camoufox core | bundled | Patched Firefox fingerprint surface (via `humanize`, `geoip`, OS presets) |

Toggle via `FoxcapeConfig`: `canvas_noise`, `audio_noise`, `hardware_spoofing`, `noise_seed`.

### Human behavior simulation

| Capability | Description |
|------------|-------------|
| **WindMouse** | `generate_windmouse_path()` — Fitts's Law mouse trajectories with inertia and micro-tremors |
| **Mouse activity** | `simulate_human_mouse_movement()` / `perform_human_activity()` — wandering, scrolling, pauses |
| **Markov cadence** | `MarkovCadence` — post-navigation dwell time modeled on scan → read → hesitate → next states |
| **Human typing** | `human_type()` — log-normal inter-key delays, dwell time, neighbor-key typos with Backspace correction |
| **Post-load cadence** | Applied automatically after `get()` when `human_delay` / `simulate_mouse` are enabled |

### Cloudflare Turnstile

- `solve_turnstile_if_present()` — detects Turnstile iframes, moves mouse organically, clicks, waits for token
- Enabled by default (`FoxcapeConfig.solve_turnstile=True`); disable per request or in config

### Proxies (`ProxyConfig`, `ProxyPoolManager`)

- Parse proxy URLs: `http://user:pass@host:port`, `socks5://...`
- Strategies: **round-robin**, **random**, **sticky** (same proxy per `session_id`)
- Converts to Playwright/Camoufox proxy dict via `to_playwright_dict()`

### Browser profiles (`ProfileManager`, `BrowserProfile`)

- Persistent `user_data_dir` — cookies, cache, and trust signals survive sessions
- Metadata tracking: age, warmth, visited domains
- **Warmup** — organic visits to trusted seed URLs (`general`, `sports`, `ecommerce`) with full human cadence before production scrapes
- `to_foxcape_config()` — one call to get a persistent `FoxcapeConfig`

### Results & parsing (`FoxcapeResult`)

Every scrape returns a rich result object:

```python
result.url           # final URL after redirects
result.html          # raw HTML
result.soup          # BeautifulSoup tree (lxml with html.parser fallback)
result.title         # <title> text
result.status_code   # HTTP status when available

result.select_one("h1")      # CSS selector — single match
result.select(".item")       # CSS selector — all matches
result.get_clean_text()      # text with scripts/nav stripped
result.to_markdown()         # headings + paragraphs → markdown (LLM-friendly)
result.extract_links()       # [{"text": "...", "href": "https://..."}, ...]
```

Standalone parsers (no browser): `build_soup`, `extract_clean_text`, `extract_links_from_soup`, `dom_to_markdown_summary`.

### Exceptions

| Exception | When |
|-----------|------|
| `FoxcapeError` | Base class for library errors |
| `BrowserStartupError` | Camoufox binaries missing or browser/page failed to start — message includes `python -m camoufox fetch` hint |

Importing `foxcape` never launches a browser or opens network connections.

---

## Installation

```bash
pip install foxcape
python -m camoufox fetch   # one-time browser download (required before first scrape)
```

---

## Quickstart

```python
from foxcape import Foxcape, FoxcapeConfig

with Foxcape(FoxcapeConfig(headless=True)) as fox:
    result = fox.get("https://example.com", human_delay=False, simulate_mouse=False)
    print(result.title)
    print(result.select_one("h1").get_text(strip=True))
```

If Camoufox binaries are missing, Foxcape raises `BrowserStartupError` with instructions to run `python -m camoufox fetch`.

---

## Usage

### Async

```python
import asyncio
from foxcape import AsyncFoxcape, FoxcapeConfig

async def main():
    config = FoxcapeConfig(headless=True, human_delay_range=None, simulate_mouse=False)
    result = await AsyncFoxcape.afetch("https://example.com", config=config)
    print(result.title)

asyncio.run(main())
```

### Proxies

```python
from foxcape import Foxcape, FoxcapeConfig, ProxyConfig, ProxyPoolManager

pool = ProxyPoolManager()
pool.add_proxy(ProxyConfig(server="http://proxy.example:8080", username="u", password="p"))

proxy = pool.get_proxy(session_id="user-123")  # sticky session
config = FoxcapeConfig(headless=True, proxy=proxy)

with Foxcape(config) as fox:
    result = fox.get("https://example.com", human_delay=False)
```

### Browser profiles & warmup

```python
from foxcape import Foxcape, ProfileManager

profile = ProfileManager.get_or_create("my_stealth_profile")
profile.warmup(category="general", steps=3)  # organic trust-building visits

config = profile.to_foxcape_config()
with Foxcape(config) as fox:
    result = fox.get("https://target.example", human_delay=True)
    print(profile.is_warm, profile.age_days)
```

Warmup categories: `general`, `sports`, `ecommerce` — each uses a curated list of high-trust seed URLs.

### JavaScript & form interaction

```python
with Foxcape(FoxcapeConfig(headless=True)) as fox:
    fox.get("https://example.com/login")
    fox.type_human("#email", "user@example.com", wpm_speed=72)
    fox.type_human("#password", "secret", typo_probability=0.02)
    token = fox.evaluate("document.querySelector('meta[name=csrf]')?.content")
```

### Custom human behavior (advanced)

Use exported helpers directly on any Playwright page:

```python
from foxcape import generate_windmouse_path, perform_human_activity, MarkovCadence

path = generate_windmouse_path(100, 200, 400, 300)  # (x, y, delay_ms) steps
sequence = MarkovCadence.generate_behavioral_sequence(max_steps=5)
dwell = MarkovCadence.calculate_reading_dwell_time(html, min_seconds=1.0, max_seconds=5.0)
```

Inject evasions on your own Camoufox pages:

```python
from foxcape import inject_fingerprint_noise, inject_hardware_and_webrtc_spoofing

inject_fingerprint_noise(page, seed=42)
inject_hardware_and_webrtc_spoofing(page)
```

---

## Configuration (`FoxcapeConfig`)

All settings have sensible stealth defaults. Common options:

| Field | Default | Purpose |
|-------|---------|---------|
| `headless` | `False` | `True`, `"virtual"`, or visible browser |
| `humanize` | `True` | Camoufox human-like cursor movement |
| `simulate_mouse` | `True` | WindMouse activity after navigation |
| `human_delay` / `human_delay_range` | `(0.5, 2.0)` | Post-load pause; set range to `None` to disable |
| `use_markov_cadence` | `True` | Markov-based dwell instead of flat random delay |
| `solve_turnstile` | `True` | Auto-detect and click Cloudflare Turnstile |
| `canvas_noise` / `audio_noise` | `True` | Fingerprint noise injection |
| `hardware_spoofing` | `True` | Navigator / WebRTC consistency overrides |
| `proxy` | `None` | `ProxyConfig`, URL string, or Playwright dict |
| `user_data_dir` | `None` | Persistent profile directory |
| `geoip` | `True` | Match timezone/locale to proxy IP |
| `os` | `"windows"` | Camoufox OS fingerprint preset |
| `wait_until` | `"domcontentloaded"` | Playwright navigation wait strategy |
| `default_timeout_ms` | `30000` | Navigation and selector timeout |
| `parser_engine` | `"lxml"` | BeautifulSoup parser (`"html.parser"` fallback) |

Full field list: see `foxcape.config.FoxcapeConfig` docstring or [Architecture](docs/ARCHITECTURE.md).

---

## Public API surface

Everything exported via `foxcape.__all__`:

**Core:** `Foxcape`, `AsyncFoxcape`, `FoxcapeConfig`, `FoxcapeResult`, `FoxcapeError`, `BrowserStartupError`

**Profiles & proxies:** `BrowserProfile`, `ProfileManager`, `ProxyConfig`, `ProxyPoolManager`

**Humanization:** `generate_windmouse_path`, `simulate_human_mouse_movement`, `async_simulate_human_mouse_movement`, `perform_human_activity`, `async_perform_human_activity`, `MarkovCadence`

**Evasions:** `get_canvas_and_audio_noise_script`, `inject_fingerprint_noise`, `async_inject_fingerprint_noise`, `get_deep_hardware_and_webrtc_spoof_script`, `inject_hardware_and_webrtc_spoofing`, `async_inject_hardware_and_webrtc_spoofing`

**Turnstile & typing:** `human_type`, `async_human_type`, `solve_turnstile_if_present`, `async_solve_turnstile_if_present`

**Parsers:** `build_soup`, `extract_clean_text`, `extract_links_from_soup`, `dom_to_markdown_summary`

Playwright and Camoufox internals are intentionally **not** exported.

---

## Development

```bash
make install          # uv sync --all-groups
make check            # format + lint + mypy + offline pytest (181 tests)
uv run pytest -m live # optional: 2 live tests; requires camoufox fetch + network
```

Offline suite: **181 tests**, ~**99%** coverage on `src/foxcape/`. Live integration tests are excluded from CI and default pytest.

Default branch: **`develop`**. See [GitFlow](docs/GITFLOW.md).

---

## Links

- [GitHub](https://github.com/andreferraro/foxcape)
- [Architecture](docs/ARCHITECTURE.md) — module map and quality gates
- [Master plan](docs/PLAN.md) — roadmap and release checklist

---

**Disclaimer:** Use responsibly. Respect site terms of service and applicable laws.
