# Foxcape

Undetectable web scraping library powered by [Camoufox](https://camoufox.com/), BeautifulSoup, and anti-bot evasions.

## Quickstart

```bash
pip install foxcape
python -m camoufox fetch   # one-time browser download (required before first scrape)
```

```python
from foxcape import Foxcape, FoxcapeConfig

with Foxcape(FoxcapeConfig(headless=True)) as fox:
    result = fox.get("https://example.com", human_delay=False, simulate_mouse=False)
    print(result.title, result.select_one("h1"))
```

If Camoufox binaries are missing, Foxcape raises `BrowserStartupError` with instructions to run `python -m camoufox fetch`.

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

### Browser profiles

```python
from foxcape import Foxcape, ProfileManager

profile = ProfileManager.get_or_create("my_stealth_profile")
config = profile.to_foxcape_config()
profile.warmup(category="general", steps=3)  # organic trust-building visits
with Foxcape(config) as fox:
    result = fox.get("https://target.example", human_delay=True)
```

## Development

```bash
make install          # uv sync --all-groups
make check            # format + lint + mypy + offline pytest (181 tests)
uv run pytest -m live # optional: 2 live tests; requires camoufox fetch + network
uv run pytest tests/test_humanizer_properties.py -v --hypothesis-show-statistics
```

Offline suite: **181 tests**, ~**99%** coverage on `src/foxcape/`. Live integration tests are excluded from CI and default pytest.

## Publishing

Release via GitFlow: `release/v0.1.0` → merge to `main` → tag `v0.1.0`. The [publish workflow](.github/workflows/publish.yml) uploads to PyPI using OIDC (configure Trusted Publisher on PyPI once).

## Layout

| Path | Purpose |
|------|---------|
| `src/foxcape/` | Library source (published to PyPI) |
| `tests/` | Offline pytest suite |
| `docs/` | [Architecture](docs/ARCHITECTURE.md), [GitFlow](docs/GITFLOW.md), [Plan](docs/PLAN.md) |
| `specs/` | SpecKit SDD artifacts |

## GitFlow

Default branch: **`develop`**. See [docs/GITFLOW.md](docs/GITFLOW.md).

## Links

- [GitHub](https://github.com/andreferraro/foxcape)
- [Architecture](docs/ARCHITECTURE.md)

**Disclaimer:** Use responsibly. Respect site ToS and applicable laws.
