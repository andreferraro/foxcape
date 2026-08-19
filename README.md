# Foxcape

Undetectable web scraping library powered by [Camoufox](https://camoufox.com/), BeautifulSoup, and anti-bot evasions.

```bash
pip install foxcape
python -m camoufox fetch   # one-time browser download
```

```python
from foxcape import Foxcape, FoxcapeConfig

with Foxcape(FoxcapeConfig(headless=True)) as fox:
    result = fox.get("https://example.com", human_delay=False, simulate_mouse=False)
    print(result.title, result.select_one("h1"))
```

## Development

```bash
make install
make check
```

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
