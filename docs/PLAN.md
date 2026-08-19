# Foxcape — Master Plan

**Versão:** 1.1  
**PyPI:** `foxcape`  
**GitHub:** https://github.com/andreferraro/foxcape  
**Import:** `from foxcape import Foxcape, FoxcapeConfig, FoxcapeResult`  
**Licença:** MIT | **Python:** `>=3.10,<4.0`

---

## 0. WORKSPACE — LEIA ANTES DE TUDO

```
┌─────────────────────────────────────────────────────────────┐
│  ESTA PASTA É O REPOSITÓRIO INTEIRO.                        │
│  Cursor workspace = stealth_scraper/ (raiz)                 │
│  A nova instância NÃO VÊ o monorepo pai.                    │
│  NÃO EXISTE specs/011 nem sandbox_scraping daqui.           │
└─────────────────────────────────────────────────────────────┘
```

| Item | Caminho (relativo à raiz do workspace) |
|---|---|
| **Este plano** | `docs/PLAN.md` |
| **Código atual (legado)** | `*.py` na raiz (`config.py`, `scraper.py`, …) |
| **Código destino** | `src/foxcape/` |
| **SpecKit spec** | `specs/001-initial-release/spec.md` |
| **SpecKit plan** | `specs/001-initial-release/plan.md` |
| **Constitution** | `.specify/memory/constitution.md` |
| **Testes** | `tests/` (criar aqui; conteúdo na seção 12) |
| **Git remote** | `https://github.com/andreferraro/foxcape.git` |

**Estado atual da raiz:** 13 módulos Python legados (`stealth_scraper` naming).  
**Trabalho:** reorganizar in-place → lib Foxcape publicável. Não clonar outro repo. Não referenciar paths do monorepo.

**Prompt inicial (nova instância Cursor nesta pasta):**

```
Leia docs/PLAN.md. Workspace = raiz desta pasta only.
Execute ciclo SpecKit SDD começando por /speckit-constitution.
Código legado = os .py na raiz; migrar para src/foxcape/ com rename Foxcape.
Não codar antes do gate /speckit-analyze.
```

---

## 1. O que é Foxcape

Biblioteca Python de scraping indetectável para **qualquer desenvolvedor** (`pip install foxcape`).

| Camada | Módulo | Função |
|---|---|---|
| Motor stealth | Camoufox | Firefox patched, anti-fingerprint C++ |
| Parsing | `parsers.py` | BeautifulSoup + lxml |
| Mouse | `humanizer.py` | WindMouse |
| Digitação | `turnstile_and_typing.py` | Biometria + Turnstile |
| Ruído | `noise_injector.py` | Canvas/WebGL/Audio |
| Hardware | `hardware_spoofing.py` | WebRTC, deviceMemory |
| Cadência | `cadence.py` | Markov dwell time |
| Perfis | `profiles.py` | Persistência + warmup |
| Proxies | `proxy_pool.py` | Round-robin, sticky |

Classes: `Foxcape` (sync), `AsyncFoxcape` (async).

---

## 2. Ciclo SpecKit SDD

Artefatos ficam **nesta pasta**, em `specs/001-initial-release/`:

```
1. /speckit-constitution  → .specify/memory/constitution.md
2. /speckit-specify       → specs/001-initial-release/spec.md
3. /speckit-clarify       → GATE
4. /speckit-plan          → plan.md, research.md, data-model.md, contracts/, quickstart.md
5. /speckit-checklist     → checklists/*.md — GATE
6. /speckit-tasks         → tasks.md
7. /speckit-analyze       → GATE — NÃO codar antes
8. /speckit-implement     → src/foxcape + tests + CI
9. /speckit-converge      → test-evidence.json + v0.1.0 PyPI
```

Gitflow: `develop` (default) → `release/v0.1.0` → `main` + tag `v0.1.0`.

Bootstrap git (se ainda não feito):

```bash
git init
git remote add origin https://github.com/andreferraro/foxcape.git
git checkout -b develop
```

---

## 3. Constitution (input `/speckit-constitution`)

```markdown
# Foxcape Library Constitution

## I. Public Library Boundary
Zero coupling to consumer apps. Runtime deps: camoufox[geoip], beautifulsoup4, lxml only.

## II. Deterministic Offline CI
pytest -m "not live" blocks merge. No network, no camoufox fetch in default CI.

## III. Camoufox-Only Engine
Playwright not in public API (__all__). Internal use only.

## IV. Ponytail / YAGNI
No mypy strict, no full Playwright exception wrap, no multi-OS browser CI v1.

## V. Stable Public API
__all__ defines public surface. Semver from 0.1.0.

Version: 1.0.0 | Ratified: 2026-08-19
```

---

## 4. Spec (input `/speckit-specify`)

### US1 — pip install + scrape (P1)

- **AC-001:** `pip install foxcape` + `python -m camoufox fetch` → scrape funciona
- **TS-001:** `import foxcape` sem side effects

### US2 — Async (P1)

- **AC-002:** `AsyncFoxcape` / `afetch` paridade com sync
- **TS-002:** `async with` fecha browser em erro

### US3 — Proxy + profiles (P2)

- **AC-003:** ProxyConfig + ProfileManager + warmup
- **TS-003:** ProxyPoolManager sticky session

### US4 — LLM extraction (P2)

- **AC-004:** `get_clean_text()`, `to_markdown()`, `extract_links()`
- **TS-004:** Scripts removidos do clean text

### US5 — CI + PyPI (P2)

- **AC-005:** CI ubuntu × py3.10–3.13, ruff+mypy+pytest offline
- **TS-005:** CI sem camoufox fetch

### FR-001..008

Pacote PyPI, __all__, context managers, exceções mínimas, mocks, README, GitHub Actions OIDC, Gitflow.

### Edge cases

camoufox fetch ausente → erro claro; lxml fallback; parent.lock stale; proxy pool vazio; warmup parcial OK.

---

## 5. Migração dos módulos (raiz → `src/foxcape/`)

**Origem:** arquivos `.py` **nesta raiz do workspace**.  
**Destino:** `src/foxcape/`. Depois **deletar** `.py` legados da raiz.

| Arquivo na raiz | Ação |
|---|---|
| `config.py` | → `FoxcapeConfig` |
| `models.py` | → `FoxcapeResult` |
| `scraper.py` | → classe `Foxcape` |
| `async_scraper.py` | → classe `AsyncFoxcape` |
| `profiles.py` | `StealthScraper`→`Foxcape`, `to_foxcape_config()`, logger `foxcape.profiles` |
| `humanizer.py`, `noise_injector.py`, `hardware_spoofing.py`, `turnstile_and_typing.py`, `cadence.py`, `parsers.py`, `proxy_pool.py` | mover, ajustar imports relativos |
| `__init__.py` | novo __all__ (seção 6), `__version__ = "0.1.0"` |
| `exceptions.py` | **criar** — FoxcapeError, BrowserStartupError |

---

## 6. API pública (`__all__`)

| Legado | Foxcape |
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

## 7. FoxcapeConfig — todos os campos

| Campo | Tipo | Default |
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

## 8. Classes principais

**FoxcapeResult:** `from_html`, `select_one`, `select`, `get_clean_text`, `extract_links`, `to_markdown`. Campos: url, html, soup, status_code, title.

**Foxcape:** `__enter__`/`__exit__`, `start`, `close`, `page`, `get`, `fetch`, `type_human`, `evaluate`.

**AsyncFoxcape:** `__aenter__`/`__aexit__`, `get_page`, `get`, `afetch`, `type_human`, `aevaluate`.

**BrowserProfile:** `warmup(category, steps)`, `to_foxcape_config()`, `is_warm`, `age_days`. Categorias warmup: general, sports, ecommerce.

**ProxyPoolManager:** `add_proxy`, `get_proxy(strategy, session_id)`.

---

## 9. Exemplos README / quickstart.md

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

Disclaimer obrigatório: uso responsável, respeitar ToS e leis.

---

## 10. Estrutura final (tudo dentro desta pasta)

```text
./                              ← workspace root (Cursor abre AQUI)
├── docs/PLAN.md                ← este arquivo
├── specs/001-initial-release/
├── .specify/memory/constitution.md
├── .github/workflows/ci.yml
├── .github/workflows/publish.yml
├── src/foxcape/                ← módulos migrados da raiz
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

## 11. pyproject.toml completo

```toml
[project]
name = "foxcape"
version = "0.1.0"
description = "Undetectable web scraping powered by Camoufox, BeautifulSoup and anti-bot evasions"
readme = "README.md"
license = "MIT"
requires-python = ">=3.10,<4.0"
authors = [{ name = "Andre Ferraro" }]
keywords = ["scraping", "camoufox", "anti-bot", "stealth", "web-scraping"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Internet :: WWW/HTTP",
    "Typing :: Typed",
]
dependencies = [
    "camoufox[geoip]>=0.5.4,<0.6.0",
    "beautifulsoup4>=4.15.0,<5.0.0",
    "lxml>=6.1.1,<7.0.0",
]

[project.urls]
Homepage = "https://github.com/andreferraro/foxcape"
Repository = "https://github.com/andreferraro/foxcape"
Issues = "https://github.com/andreferraro/foxcape/issues"

[build-system]
requires = ["hatchling>=1.27.0"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/foxcape"]

[dependency-groups]
dev = ["pytest>=9", "pytest-asyncio>=1.4", "ruff>=0.9", "mypy>=1.15", "pre-commit>=4"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-m 'not live' -v"
asyncio_mode = "auto"
markers = ["live: requires camoufox browser and network"]

[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP"]

[tool.mypy]
python_version = "3.10"
check_untyped_defs = true
ignore_missing_imports = true
```

---

## 12. Testes (criar em `tests/` nesta pasta)

### conftest.py

```python
import pytest
from foxcape import FoxcapeConfig

SAMPLE_HTML = """<!DOCTYPE html><html><head><title>Test Page</title></head>
<body><header><nav><a href="/home">Home</a></nav></header>
<main><h1>Main Heading</h1><p>Paragraph<script>console.log("x");</script></p></main>
</body></html>"""

@pytest.fixture
def default_config():
    return FoxcapeConfig(headless=True, humanize=False, simulate_mouse=False)

@pytest.fixture
def sample_html():
    return SAMPLE_HTML
```

### test_config.py

Defaults: headless=False, humanize=True, simulate_mouse=True, canvas/audio/hardware/turnstile/markov=True, geoip=True, wait_until=domcontentloaded, timeout=30000, parser=lxml.

### test_models.py

`FoxcapeResult.from_html(SAMPLE_HTML)` → title "Test Page", h1 "Main Heading", 3 links, clean text sem console.log, markdown com heading.

### test_humanizer.py

`generate_windmouse_path(100,100,500,400)` → len>5, final point (500,400), delay>0.

### test_public_api.py

`__version__`, exports Foxcape/AsyncFoxcape/FoxcapeConfig/FoxcapeResult/ProfileManager; ProxyPoolManager round_robin + sticky.

### test_foxcape.py / test_async_foxcape.py

Mock `camoufox.sync_api.Camoufox` / `AsyncCamoufox` — fake page, goto status 200, lifecycle with context manager.

### test_integration.py

`@pytest.mark.live` — example.com sync+async; **fora do CI default**.

---

## 13. CI/CD

**ci.yml:** push/PR em develop+main; matrix py3.10–3.13 ubuntu; uv sync; ruff; mypy src/foxcape; pytest.

**publish.yml:** tag v*; uv build; pypa/gh-action-pypi-publish OIDC.

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

## 15. pre-commit

ruff + ruff-format + trailing-whitespace + end-of-file-fixer + check-yaml + check-toml.

---

## 16. tasks.md (input `/speckit-tasks`)

### Phase 1 — Bootstrap

- T001 pyproject.toml, uv.lock, .gitignore, LICENSE MIT
- T002 src/foxcape/py.typed + hatchling layout
- T003 .specify/ + specs/001-initial-release/
- T004 pre-commit, ruff, mypy, pytest markers
- T005 git init + remote origin + branch develop

### Phase 2 — Migrar código (raiz → src/foxcape)

- T006 Mover config.py → FoxcapeConfig
- T007 Mover models.py → FoxcapeResult
- T008 Criar exceptions.py
- T009 Mover proxy_pool, parsers, cadence, humanizer, noise, hardware, turnstile
- T010 Mover scraper.py → Foxcape
- T011 Mover async_scraper.py → AsyncFoxcape
- T012 Mover profiles.py + renames
- T013 Montar __init__.py __all__
- T014 Remover .py legados da raiz

### Phase 3 — Testes

- T015 Criar tests/ (seção 12)
- T016 Mocks Camoufox
- T17 pytest offline verde

### Phase 4 — Publish

- T018 README + quickstart
- T019 GitHub Actions
- T020 PyPI Trusted Publisher
- T021 Release v0.1.0

### Phase 5 — Converge

- T022 speckit-converge + test-evidence.json

---

## 17. research.md (decisões)

| Decisão | Escolha |
|---|---|
| PyPI name | foxcape (stealth-scraper ocupado) |
| Build | hatchling + PEP 621 |
| PM | uv |
| Layout | src/foxcape |
| Python | >=3.10 |
| Mypy | pragmático |
| CI OS | ubuntu only |

---

## 18. Checklist Gemini

**Sim:** src layout, hatchling, uv, py.typed, __all__, exceções mínimas, ruff, pre-commit, pytest+mock, README, CI ubuntu×py3.10–3.13, OIDC, Gitflow.

**Não:** mypy strict, CI multi-OS browser, wrap all Playwright, Sphinx, aliases stealth_scraper.

---

## 19. Fora de escopo deste repo

Integração com monorepo/workers/RabbitMQ/PostgreSQL. Consumidores legados trocam `stealth_scraper` por `foxcape` depois do PyPI — não documentar aqui.
