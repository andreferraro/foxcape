# Public API Contract: foxcape v0.1.0

Stable surface defined by `foxcape.__all__`. Breaking changes require semver bump.

## Package metadata

- **Name**: `foxcape`
- **Version**: `0.1.0`
- **Python**: `>=3.10,<4.0`
- **Typed**: yes (`py.typed`)

## Exported symbols

### Core types

| Symbol | Kind | Contract |
|--------|------|----------|
| `FoxcapeConfig` | dataclass | Immutable config snapshot; all fields have documented defaults |
| `FoxcapeResult` | dataclass | Parse helpers must not mutate input HTML |
| `Foxcape` | class | Sync context manager; idempotent `close()` |
| `AsyncFoxcape` | class | Async context manager; `afetch` classmethod |
| `FoxcapeError` | exception | Base for library errors |
| `BrowserStartupError` | exception | Raised when browser/page fails to start |

### Profiles & proxies

| Symbol | Contract |
|--------|----------|
| `BrowserProfile` | `to_foxcape_config()` returns config with `user_data_dir` set |
| `ProfileManager` | `get_or_create(name)` is idempotent |
| `ProxyConfig` | `from_url` parses http/socks URLs; `to_playwright_dict()` for Camoufox |
| `ProxyPoolManager` | `get_proxy(session_id=...)` sticky; round-robin without session_id |

### Humanization & evasion (advanced)

Exported functions for custom integrations: `generate_windmouse_path`, mouse/activity simulators, noise injectors, hardware spoofing scripts, Turnstile helpers, `MarkovCadence`, parser utilities (`build_soup`, `extract_clean_text`, etc.).

## Import contract

```python
import foxcape  # MUST NOT launch browser or perform network I/O
```

## Non-exported (internal)

- `camoufox`, `playwright` modules
- Private helpers and `_`-prefixed attributes

## Versioning

Semver from 0.1.0. Pre-1.0: minor bumps may add API; patch for fixes.
