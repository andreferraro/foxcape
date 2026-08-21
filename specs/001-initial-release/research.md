# Research: Foxcape Initial Release

**Date**: 2026-08-19
**Feature**: 001-initial-release

## Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| PyPI name | `foxcape` | `stealth-scraper` taken; matches GitHub repo |
| Build backend | hatchling + PEP 621 | Standard for typed Python libs; lightweight |
| Package manager | uv | Fast lockfile, CI-friendly, matches Makefile |
| Layout | `src/foxcape` | Import isolation, PyPI best practice |
| Python support | >=3.10, <4.0 | Camoufox + typing compatibility |
| Type checking | mypy pragmatic | Constitution IV — not strict mode |
| CI matrix | ubuntu × py3.10–3.13 | Constitution — no multi-OS browser CI v1 |
| Browser engine | Camoufox only | Constitution III; anti-detect focus |
| Offline testing | Mock Camoufox at import boundary | Constitution II; no fetch in CI |
| Live tests | `@pytest.mark.live` opt-in | Manual/staging validation only |
| Publishing | PyPI trusted publisher (OIDC) | No long-lived PyPI passwords in GitHub |
| Branching | Gitflow, default `develop` | PLAN + team convention |
| Public API | `__all__` + semver 0.1.0 | Constitution V |
| Legacy naming | No `stealth_scraper` aliases | YAGNI — clean break on PyPI |

## Alternatives Considered

| Alternative | Rejected because |
|-------------|------------------|
| Flat layout (modules at root) | Poor PyPI hygiene; already migrated to src/ |
| Playwright in public API | Violates constitution; leaks implementation |
| mypy strict | Constitution IV; disproportionate for v0.1.0 |
| Docker-based CI with browser | Network + complexity; deferred |
| setuptools | hatchling simpler for pure Python wheel |

## Open Questions

None — all resolved via PLAN.md and clarification session 2026-08-19.
