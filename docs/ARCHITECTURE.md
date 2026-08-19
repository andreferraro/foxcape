# Architecture — Foxcape

Publishable Python library (`pip install foxcape`). No coupling to consumer applications.

## Repository layout

```text
foxcape/
├── src/foxcape/          # library code (only package published to PyPI)
├── tests/                # pytest (offline by default; live opt-in)
├── docs/                 # plan, gitflow, architecture
├── specs/                # SpecKit SDD artifacts
├── .specify/             # SpecKit infrastructure (templates, scripts)
├── .cursor/              # Cursor MCP + skills
├── .agents/skills/       # installed agent skills (SpecKit, Graphify, Ponytail)
├── .github/workflows/    # CI, publish, SonarQube
├── pyproject.toml        # PEP 621 + hatchling
├── Makefile              # local quality gates
└── README.md
```

**Rule:** no library Python modules at the repo root. Everything lives under `src/foxcape/`.

## Internal layers (`src/foxcape/`)

| Module | Responsibility |
|--------|----------------|
| `scraper.py` / `async_scraper.py` | Sync/async facade (`Foxcape`, `AsyncFoxcape`) — Camoufox lifecycle |
| `camoufox_launch.py` | Shared launch kwargs, page resolution, evasion injection |
| `scrape_cadence.py` | Post-navigation human delay / mouse activity |
| `config.py` | `FoxcapeConfig` — settings dataclass |
| `models.py` | `FoxcapeResult` — parsed HTML + LLM helpers |
| `exceptions.py` | `FoxcapeError`, `BrowserStartupError` |
| `humanizer.py` | WindMouse paths + organic browsing activity |
| `cadence.py` | Markov dwell-time simulator |
| `noise_injector.py` | Canvas / WebGL / audio fingerprint noise |
| `hardware_spoofing.py` | WebRTC, deviceMemory, permissions consistency |
| `turnstile_and_typing.py` | Cloudflare Turnstile + biometric typing |
| `parsers.py` | BeautifulSoup / lxml extraction |
| `profiles.py` | Persistent browser profiles + warmup |
| `proxy_pool.py` | Round-robin / random / sticky proxy pool |
| `rng.py` | Non-cryptographic randomness for human-like behavior |
| `__init__.py` | Public API via `__all__` |

## Public API

Defined exclusively by `foxcape.__all__`. Playwright/Camoufox internals are **not** exported.

```python
from foxcape import Foxcape, FoxcapeConfig, FoxcapeResult
```

See [specs/001-initial-release/contracts/public-api.md](../specs/001-initial-release/contracts/public-api.md).

## Runtime dependencies

- `camoufox[geoip]` — stealth browser engine (sole engine)
- `beautifulsoup4` + `lxml` — HTML parsing

## Quality gates

| Gate | Command | Notes |
|------|---------|-------|
| Full check | `make check` | format + lint + mypy + offline pytest |
| Offline tests | `pytest` | excludes `@pytest.mark.live` by default |
| Live tests | `pytest -m live` | requires `python -m camoufox fetch` + network |
| Lint/format | `ruff check` / `ruff format` | src + tests |
| Types | `mypy src/foxcape` | pragmatic (not strict) |

**CI:** Ubuntu × Python 3.10–3.13; no Camoufox download; no network in default pytest.

**YAGNI (v0.1.0):** no strict mypy, no multi-OS browser CI, no legacy `stealth_scraper` aliases.

## Test suite (offline)

126 offline tests + 2 live integration tests (`test_integration.py`). Coverage ~96% on `src/foxcape/` (see `specs/001-initial-release/test-evidence.json`).

Categories: unit (parsers, proxy, cadence), mocked integration (sync/async scraper, turnstile, profiles), contract/smoke, Hypothesis property tests (`test_humanizer_properties.py`).

## Agent tooling (outside the PyPI wheel)

Skills under `.agents/skills/` and `.cursor/skills/` are **not** packaged. Graphify installs its runtime via `uv tool install graphify` when invoked.
