# Arquitetura — Foxcape

Biblioteca Python publicável (`pip install foxcape`). Zero acoplamento com apps consumidoras.

## Layout do repositório

```text
foxcape/
├── src/foxcape/          # código da lib (único pacote publicado)
├── tests/                # pytest offline por padrão
├── docs/                 # plano, gitflow, arquitetura
├── specs/                # artefatos SpecKit (SDD)
├── .specify/             # infra SpecKit (templates, scripts)
├── .cursor/              # MCP + skills Cursor
├── .agents/skills/       # skills instaladas (SpecKit, Graphify, Ponytail)
├── .github/workflows/    # CI
├── pyproject.toml        # PEP 621 + hatchling
├── Makefile              # quality gates locais
└── README.md
```

**Regra:** nenhum módulo Python da lib na raiz do repo. Tudo vive em `src/foxcape/`.

## Camadas internas (`src/foxcape/`)

| Módulo | Responsabilidade |
|--------|------------------|
| `scraper.py` / `async_scraper.py` | Facade sync/async (`Foxcape`, `AsyncFoxcape`) — lifecycle Camoufox |
| `config.py` | `FoxcapeConfig` — dataclass de configuração |
| `models.py` | `FoxcapeResult` — HTML parseado + helpers LLM |
| `exceptions.py` | `FoxcapeError`, `BrowserStartupError` |
| `humanizer.py` | WindMouse + atividade humana |
| `cadence.py` | Markov dwell time |
| `noise_injector.py` | Canvas/WebGL/Audio noise |
| `hardware_spoofing.py` | WebRTC, deviceMemory |
| `turnstile_and_typing.py` | Turnstile + digitação biométrica |
| `parsers.py` | BeautifulSoup / lxml |
| `profiles.py` | Perfis persistentes + warmup |
| `proxy_pool.py` | Pool round-robin / sticky |
| `__init__.py` | API pública via `__all__` |

## API pública

Definida exclusivamente por `foxcape.__all__`. Playwright/Camoufox internals **não** são exportados.

```python
from foxcape import Foxcape, FoxcapeConfig, FoxcapeResult
```

## Dependências runtime

- `camoufox[geoip]` — motor stealth (único browser engine)
- `beautifulsoup4` + `lxml` — parsing

## Quality gates

- **Offline CI:** `pytest -m "not live"` — sem rede, sem `camoufox fetch`
- **Lint/format:** ruff
- **Types:** mypy pragmático (não strict)
- **YAGNI:** Ponytail constitution — sem mypy strict, sem CI multi-OS browser v1

## Agent tooling (fora do pacote PyPI)

Skills em `.agents/skills/` e `.cursor/skills/` **não** entram no wheel. Graphify instala runtime via `uv tool install graphify` quando invocado.
