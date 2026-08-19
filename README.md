# Foxcape

Undetectable web scraping library powered by [Camoufox](https://camoufox.com/), BeautifulSoup, and anti-bot evasions.

**Status:** bootstrap — legacy modules at repo root; migration to `src/foxcape/` in progress. See [`docs/PLAN.md`](docs/PLAN.md).

## Quick start (dev)

```bash
make install
make check
```

## GitFlow

| Branch | Purpose |
|--------|---------|
| `develop` | default integration branch |
| `feature/*` | new work |
| `release/*` | release prep |
| `main` | production releases (tags `v*`) |

## Agent tooling

- **SpecKit** — SDD workflow (`/speckit-constitution`, `/speckit-specify`, …)
- **Graphify** — codebase knowledge graph (`/graphify`)
- **Ponytail** — YAGNI / scope guard (`/ponytail`)
- **GitHub MCP** — `.cursor/mcp.json` (set `GITHUB_TOKEN` in `.env` or system env)

## Links

- [GitHub](https://github.com/andreferraro/foxcape)
- [Master plan](docs/PLAN.md)
