# Foxcape — Master Plan

**Version:** 1.2  
**PyPI:** `foxcape`  
**GitHub:** https://github.com/andreferraro/foxcape  
**Import:** `from foxcape import Foxcape, FoxcapeConfig, FoxcapeResult`  
**License:** MIT | **Python:** `>=3.10,<4.0`

---

## 0. WORKSPACE — READ FIRST

```
┌─────────────────────────────────────────────────────────────┐
│  THIS FOLDER IS THE ENTIRE REPOSITORY.                      │
│  Cursor workspace = repo root                               │
│  Self-contained — no parent monorepo paths.                 │
└─────────────────────────────────────────────────────────────┘
```

| Item | Path (relative to workspace root) |
|---|---|
| **This plan** | `docs/PLAN.md` |
| **Library source** | `src/foxcape/` |
| **SpecKit spec** | `specs/001-initial-release/spec.md` |
| **SpecKit plan** | `specs/001-initial-release/plan.md` |
| **Constitution** | `.specify/memory/constitution.md` |
| **Tests** | `tests/` (see section 12) |
| **Git remote** | `https://github.com/andreferraro/foxcape.git` |

**Current state:** library lives under `src/foxcape/` with Foxcape public API. Root legacy modules removed.  
**Remaining work:** SpecKit SDD artifacts, Camoufox mocks, publish workflow, PyPI release.

**Initial prompt (new Cursor instance in this folder):**

```
Read docs/PLAN.md. Workspace = this folder root only.
Run SpecKit SDD cycle starting with /speckit-specify (constitution already ratified).
Do not implement features before the /speckit-analyze gate.
```

---

## 1. What is Foxcape

Undetectable Python scraping library for **any developer** (`pip install foxcape`).

| Layer | Module | Role |
|---|---|---|
| Stealth engine | Camoufox | Patched Firefox, anti-fingerprint C++ |
| Parsing | `parsers.py` | BeautifulSoup + lxml |
| Mouse | `humanizer.py` | WindMouse |
| Typing | `turnstile_and_typing.py` | Biometrics + Turnstile |
| Noise | `noise_injector.py` | Canvas/WebGL/Audio |
| Hardware | `hardware_spoofing.py` | WebRTC, deviceMemory |
| Cadence | `cadence.py` | Markov dwell time |
| Profiles | `profiles.py` | Persistence + warmup |
| Proxies | `proxy_pool.py` | Round-robin, sticky |

Classes: `Foxcape` (sync), `AsyncFoxcape` (async).

---

## 2. SpecKit SDD cycle

Artifacts live **in this repo** under `specs/001-initial-release/`:

```
1. /speckit-constitution  → .specify/memory/constitution.md  [DONE]
2. /speckit-specify       → specs/001-initial-release/spec.md  [DONE]
3. /speckit-clarify       → GATE                             [DONE]
4. /speckit-plan          → plan.md, research.md, data-model.md, contracts/, quickstart.md  [DONE]
5. /speckit-checklist     → checklists/*.md — GATE           [DONE]
6. /speckit-tasks         → tasks.md                         [DONE]
7. /speckit-analyze       → GATE — DO NOT code before approval [DONE — see summary below]
8. /speckit-implement     → remaining tasks in tasks.md
9. /speckit-converge      → test-evidence.json + v0.1.0 PyPI
```

Gitflow: `develop` (default) → `release/v0.1.0` → `main` + tag `v0.1.0`.

---

## 3. Constitution (input `/speckit-constitution`) — DONE

See `.specify/memory/constitution.md`.

---

## 4. Spec (input `/speckit-specify`)

### US1 — pip install + scrape (P1)

- **AC-001:** `pip install foxcape` + `python -m camoufox fetch` → scrape works
- **TS-001:** `import foxcape` has no side effects

### US2 — Async (P1)

- **AC-002:** `AsyncFoxcape` / `afetch` parity with sync
- **TS-002:** `async with` closes browser on error

### US3 — Proxy + profiles (P2)

- **AC-003:** ProxyConfig + ProfileManager + warmup
- **TS-003:** ProxyPoolManager sticky session

### US4 — LLM extraction (P2)

- **AC-004:** `get_clean_text()`, `to_markdown()`, `extract_links()`
- **TS-004:** Scripts removed from clean text

### US5 — CI + PyPI (P2)

- **AC-005:** CI ubuntu × py3.10–3.13, ruff+mypy+pytest offline
- **TS-005:** CI without camoufox fetch

### FR-001..008

PyPI package, __all__, context managers, minimal exceptions, mocks, README, GitHub Actions OIDC, Gitflow.

### Edge cases

Missing camoufox fetch → clear error; lxml fallback; stale parent.lock; empty proxy pool; partial warmup OK.

---

## 5. Module migration (root → `src/foxcape/`) — DONE

| Source (legacy root) | Action |
|---|---|
| `config.py` | → `FoxcapeConfig` |
| `models.py` | → `FoxcapeResult` |
| `scraper.py` | → `Foxcape` class |
| `async_scraper.py` | → `AsyncFoxcape` class |
| `profiles.py` | `StealthScraper`→`Foxcape`, `to_foxcape_config()`, logger `foxcape.profiles` |
| `humanizer.py`, `noise_injector.py`, `hardware_spoofing.py`, `turnstile_and_typing.py`, `cadence.py`, `parsers.py`, `proxy_pool.py` | moved, relative imports |
| `__init__.py` | public __all__ (section 6), `__version__ = "0.1.0"` |
| `exceptions.py` | **created** — FoxcapeError, BrowserStartupError |

---

## 6. Public API (`__all__`)

| Legacy | Foxcape |
|---|---|
| `StealthScraper` | `Foxcape` |
| `AsyncStealthScraper` | `AsyncFoxcape` |
| `ScraperConfig` | `FoxcapeConfig` |
| `ScrapeResult` | `FoxcapeResult` |
| `to_scraper_config()` | `to_foxcape_config()` |

```python
__all__ = [
    "FoxcapeConfig", "FoxcapeResult", "Foxcape", "AsyncFoxcape",
    "FoxcapeError", "BrowserStartupError",
    "generate_windmouse_path", "simulate_human_mouse_movement",
    "async_simulate_human_mouse_movement", "perform_human_activity",
    "async_perform_human_activity", "get_canvas_and_audio_noise_script",
    "inject_fingerprint_noise", "async_inject_fingerprint_noise",
    "get_deep_hardware_and_webrtc_spoof_script",
    "inject_hardware_and_webrtc_spoofing", "async_inject_hardware_and_webrtc_spoofing",
    "human_type", "async_human_type", "solve_turnstile_if_present",
    "async_solve_turnstile_if_present", "MarkovCadence",
    "BrowserProfile", "ProfileManager", "ProxyConfig", "ProxyPoolManager",
    "build_soup", "extract_clean_text", "extract_links_from_soup",
    "dom_to_markdown_summary",
]
```

---

## 7. FoxcapeConfig — all fields

| Field | Type | Default |
|---|---|---|
| headless | bool \| "virtual" | False |
| humanize | bool \| float | True |
| simulate_mouse | bool | True |
| canvas_noise | bool | True |
| audio_noise | bool | True |
| hardware_spoofing | bool | True |
| solve_turnstile | bool | True |
| use_markov_cadence | bool | True |
| noise_seed | int \| None | None |
| fingerprint_preset | bool \| dict \| None | None |
| geoip | bool \| str | True |
| geoip_db | str \| None | None |
| os | str \| list \| None | "windows" |
| disable_coop | bool | False |
| i_know_what_im_doing | bool | False |
| block_images | bool | False |
| block_webrtc | bool | False |
| block_webgl | bool | False |
| enable_cache | bool | False |
| user_data_dir | Path \| str \| None | None |
| persistent_context | bool | False |
| proxy | dict \| ProxyConfig \| str \| None | None |
| window | tuple \| None | None |
| locale | str \| list \| None | None |
| fonts | list \| None | None |
| wait_until | Literal | "domcontentloaded" |
| default_timeout_ms | int | 30000 |
| human_delay_range | tuple | (0.5, 2.0) |
| parser_engine | str | "lxml" |

---

## 8. Core classes

**FoxcapeResult:** `from_html`, `select_one`, `select`, `get_clean_text`, `extract_links`, `to_markdown`. Fields: url, html, soup, status_code, title.

**Foxcape:** `__enter__`/`__exit__`, `start`, `close`, `page`, `get`, `fetch`, `type_human`, `evaluate`.

**AsyncFoxcape:** `__aenter__`/`__aexit__`, `get_page`, `get`, `afetch`, `type_human`, `aevaluate`.

**BrowserProfile:** `warmup(category, steps)`, `to_foxcape_config()`, `is_warm`, `age_days`. Warmup categories: general, sports, ecommerce.

**ProxyPoolManager:** `add_proxy`, `get_proxy(strategy, session_id)`.

---

## 9. README / quickstart examples

```bash
pip install foxcape
python -m camoufox fetch
```

```python
from foxcape import Foxcape, FoxcapeConfig

with Foxcape(FoxcapeConfig(headless=True)) as fox:
    r = fox.get("https://example.com", human_delay=False, simulate_mouse=False)
    print(r.title, r.select_one("h1"))
```

```python
from foxcape import AsyncFoxcape
import asyncio
async def main():
    async with AsyncFoxcape() as fox:
        print((await fox.get("https://example.com")).title)
asyncio.run(main())
```

```python
from foxcape import Foxcape, FoxcapeConfig, ProxyConfig
cfg = FoxcapeConfig(proxy=ProxyConfig.from_url("http://u:p@host:8080"), geoip=True)
with Foxcape(cfg) as fox:
    print(fox.get("https://httpbin.org/ip").get_clean_text())
```

```python
from foxcape import ProfileManager, Foxcape
p = ProfileManager.get_or_create("prod")
if not p.is_warm: p.warmup(steps=2)
with Foxcape(p.to_foxcape_config()) as fox:
    print(fox.get("https://example.com").title)
```

Required disclaimer: use responsibly; respect site ToS and applicable laws.

---

## 10. Final structure (everything in this repo)

```text
./                              ← workspace root
├── docs/PLAN.md                ← this file
├── docs/ARCHITECTURE.md
├── docs/GITFLOW.md
├── specs/001-initial-release/
├── .specify/memory/constitution.md
├── .github/workflows/ci.yml
├── .github/workflows/publish.yml   ← TODO
├── src/foxcape/
│   ├── __init__.py
│   ├── py.typed
│   └── ...
├── tests/
├── LICENSE
├── README.md
├── pyproject.toml
├── uv.lock
└── .pre-commit-config.yaml
```

---

## 11. pyproject.toml (reference)

See root `pyproject.toml` for the live config (hatchling, uv dev groups, ruff, mypy, pytest markers).

---

## 12. Tests (`tests/`)

### conftest.py — DONE

Shared fixtures: `default_config`, `sample_html`.

### test_config.py — DONE

Default values for FoxcapeConfig fields.

### test_models.py — DONE

`FoxcapeResult.from_html` parsing, clean text, markdown.

### test_humanizer.py — TODO

`generate_windmouse_path(100,100,500,400)` → len>5, final point (500,400), delay>0.

### test_public_api.py — DONE

`__version__`, exports, ProxyPoolManager round_robin + sticky.

### test_foxcape.py / test_async_foxcape.py — TODO

Mock `camoufox.sync_api.Camoufox` / `AsyncCamoufox` — fake page, goto status 200, context manager lifecycle.

### test_integration.py — TODO

`@pytest.mark.live` — example.com sync+async; **excluded from default CI**.

---

## 13. CI/CD

**ci.yml:** DONE — push/PR on develop+main; matrix py3.10–3.13 ubuntu; uv sync; ruff; mypy; pytest.

**publish.yml:** TODO — tag v*; uv build; pypa/gh-action-pypi-publish OIDC.

**PyPI Trusted Publisher:** owner `andreferraro`, repo `foxcape`, workflow `publish.yml`.

---

## 14. Gitflow + release v0.1.0

```bash
git checkout develop
git checkout -b release/v0.1.0
git checkout main && git merge --no-ff release/v0.1.0
git tag v0.1.0
git checkout develop && git merge --no-ff release/v0.1.0
git push origin main develop --tags
```

---

## 15. pre-commit — DONE

ruff + ruff-format + trailing-whitespace + end-of-file-fixer + check-yaml + check-toml.

---

## 16. tasks.md (input `/speckit-tasks`)

### Phase 1 — Bootstrap — DONE

- T001 pyproject.toml, uv.lock, .gitignore, LICENSE MIT
- T002 src/foxcape/py.typed + hatchling layout
- T003 .specify/ + specs/001-initial-release/
- T004 pre-commit, ruff, mypy, pytest markers
- T005 git init + remote origin + branch develop

### Phase 2 — Migrate code (root → src/foxcape) — DONE

- T006–T014 module migration and Foxcape renames

### Phase 3 — Tests — PARTIAL

- T015 tests/ scaffold — DONE
- T016 Camoufox mocks — TODO
- T17 offline pytest green — DONE (baseline)

### Phase 4 — Publish — TODO

- T018 README + quickstart
- T019 GitHub Actions publish workflow
- T020 PyPI Trusted Publisher
- T021 Release v0.1.0

### Phase 5 — Converge — TODO

- T022 speckit-converge + test-evidence.json

---

## 17. research.md (decisions)

| Decision | Choice |
|---|---|
| PyPI name | foxcape (stealth-scraper taken) |
| Build | hatchling + PEP 621 |
| PM | uv |
| Layout | src/foxcape |
| Python | >=3.10 |
| Mypy | pragmatic |
| CI OS | ubuntu only |

---

## 18. Scope checklist

**In scope:** src layout, hatchling, uv, py.typed, __all__, minimal exceptions, ruff, pre-commit, pytest+mock, README, CI ubuntu×py3.10–3.13, OIDC, Gitflow.

**Out of scope v1:** mypy strict, multi-OS browser CI, wrap all Playwright errors, Sphinx, stealth_scraper aliases.

---

## 19. Out of scope for this repo

Integration with monorepo/workers/RabbitMQ/PostgreSQL. Legacy consumers switch from `stealth_scraper` to `foxcape` after PyPI — not documented here.
