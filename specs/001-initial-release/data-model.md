# Data Model: Foxcape Initial Release

**Date**: 2026-08-19

## Entities

### FoxcapeConfig

Configuration for a scrape session. Dataclass with defaults for stealth, timing, proxy, and browser options.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| headless | bool \| "virtual" | False | Browser visibility |
| humanize | bool \| float | True | Human-like timing |
| simulate_mouse | bool | True | WindMouse activity |
| canvas_noise | bool | True | Canvas fingerprint noise |
| audio_noise | bool | True | Audio fingerprint noise |
| hardware_spoofing | bool | True | WebRTC/hardware spoof |
| solve_turnstile | bool | True | Auto-solve Turnstile |
| use_markov_cadence | bool | True | Markov dwell timing |
| noise_seed | int \| None | None | Deterministic noise seed |
| fingerprint_preset | bool \| dict \| None | None | Camoufox fingerprint |
| geoip | bool \| str | True | GeoIP alignment |
| geoip_db | str \| None | None | Custom GeoIP DB path |
| os | str \| list \| None | "windows" | OS fingerprint |
| disable_coop | bool | False | COOP disable flag |
| i_know_what_im_doing | bool | False | Acknowledge risky opts |
| block_images | bool | False | Block image loads |
| block_webrtc | bool | False | Block WebRTC |
| block_webgl | bool | False | Block WebGL |
| enable_cache | bool | False | Browser cache |
| user_data_dir | Path \| str \| None | None | Profile directory |
| persistent_context | bool | False | Persistent browser ctx |
| proxy | dict \| ProxyConfig \| str \| None | None | Proxy configuration |
| window | tuple \| None | None | Window size |
| locale | str \| list \| None | None | Browser locale |
| fonts | list \| None | None | Font list |
| wait_until | Literal | "domcontentloaded" | Navigation wait |
| default_timeout_ms | int | 30000 | Default timeout |
| human_delay_range | tuple | (0.5, 2.0) | Delay bounds |
| parser_engine | str | "lxml" | BS4 parser |

### FoxcapeResult

Output of a successful page fetch.

| Field | Type | Description |
|-------|------|-------------|
| url | str | Final URL after redirects |
| html | str | Raw page HTML |
| soup | BeautifulSoup | Parsed DOM |
| status_code | int \| None | HTTP status |
| title | str | Document title |

**Methods**: `from_html`, `select_one`, `select`, `get_clean_text`, `extract_links`, `to_markdown`

### ProxyConfig

| Field | Type | Description |
|-------|------|-------------|
| server | str | Proxy URL (scheme://host:port) |
| username | str \| None | Auth user |
| password | str \| None | Auth password |
| protocol | str | Scheme (http, socks5, …) |

**Methods**: `from_url`, `to_playwright_dict`

### ProxyPoolManager

In-memory pool with round-robin index and sticky session map.

| State | Type | Description |
|-------|------|-------------|
| _proxies | list[ProxyConfig] | Registered proxies |
| _sticky_sessions | dict[str, ProxyConfig] | session_id → proxy |
| _index | int | Round-robin cursor |

### BrowserProfile

Filesystem-backed profile under `.profiles/{name}/`.

| Metadata key | Type | Description |
|--------------|------|-------------|
| name | str | Profile identifier |
| created_at | ISO datetime | Creation time |
| last_used_at | ISO datetime | Last access |
| visited_urls_count | int | Warmup/history counter |
| warmup_completed | bool | Warmth flag |
| warmup_category | str \| None | Last warmup category |
| visited_domains | list[str] | Domains visited |

**Methods**: `warmup`, `to_foxcape_config`, `clean_lock`, `is_warm`, `age_days`

### Exceptions

- `FoxcapeError` — base library error
- `BrowserStartupError(FoxcapeError)` — Camoufox/page init failure

## Relationships

```text
FoxcapeConfig ──uses──▶ ProxyConfig (optional)
BrowserProfile ──produces──▶ FoxcapeConfig
Foxcape / AsyncFoxcape ──produces──▶ FoxcapeResult
ProxyPoolManager ──provides──▶ ProxyConfig
ProfileManager ──manages──▶ BrowserProfile
```

## State Transitions

### Foxcape lifecycle

```text
[unstarted] ──start()──▶ [browser open] ──get/fetch──▶ [FoxcapeResult]
                │                              │
                └──close()/__exit__──▶ [unstarted]
```

### BrowserProfile warmth

```text
[cold] ──warmup()──▶ [warm] ──to_foxcape_config()──▶ FoxcapeConfig(persistent)
```
