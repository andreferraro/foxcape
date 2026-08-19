# Implementation Plan: Foxcape Initial Release

**Branch**: `001-initial-release` | **Date**: 2026-08-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-initial-release/spec.md`

## Summary

Ship Foxcape v0.1.0 as a typed, publishable Python library (`src/foxcape`) with sync/async Camoufox scrapers, proxy/profile support, LLM extraction helpers, offline CI on Ubuntu × Python 3.10–3.13, and PyPI trusted publishing. Bootstrap and module migration are complete; remaining work is Camoufox test mocks, publish workflow, and release validation.

## Technical Context

**Language/Version**: Python 3.10–3.13 (pinned 3.12 for local dev via `.python-version`)

**Primary Dependencies**: camoufox[geoip]>=0.5.4, beautifulsoup4>=4.15, lxml>=6.1 (runtime); pytest, ruff, mypy, pre-commit (dev)

**Storage**: Filesystem — browser profiles under `.profiles/`, Camoufox cache under `.camoufox/` (gitignored)

**Testing**: pytest + pytest-asyncio; `@pytest.mark.live` for browser/network; default CI excludes live

**Target Platform**: Linux CI (ubuntu-latest); library consumable on any OS where Camoufox runs

**Project Type**: Python library (hatchling wheel, PEP 621)

**Performance Goals**: N/A for v0.1.0 library release (no SLA targets)

**Constraints**: Offline CI must not fetch Camoufox or hit network; public API via `__all__` only; Playwright not exported

**Scale/Scope**: Single package ~15 modules; 7+ offline tests; one PyPI release 0.1.0

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Public Library Boundary | PASS | Runtime deps limited to camoufox, bs4, lxml |
| II. Deterministic Offline CI | PASS | pytest `-m "not live"`; CI has no camoufox fetch |
| III. Camoufox-Only Engine | PASS | Playwright used internally only |
| IV. Ponytail / YAGNI | PASS | Pragmatic mypy; ubuntu-only CI; minimal exceptions |
| V. Stable Public API | PASS | `__all__` in `src/foxcape/__init__.py`, semver 0.1.0 |

**Post-design re-check**: PASS — no constitution violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/001-initial-release/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── public-api.md
├── checklists/
│   ├── requirements.md
│   └── release-gate.md
└── tasks.md
```

### Source Code (repository root)

```text
src/foxcape/
├── __init__.py          # __all__, __version__
├── config.py            # FoxcapeConfig
├── models.py            # FoxcapeResult
├── scraper.py           # Foxcape (sync)
├── async_scraper.py     # AsyncFoxcape
├── camoufox_launch.py   # shared launch + evasion injection
├── scrape_cadence.py    # post-navigation human cadence
├── rng.py               # non-crypto randomness
├── exceptions.py
├── humanizer.py
├── cadence.py
├── noise_injector.py
├── hardware_spoofing.py
├── turnstile_and_typing.py
├── parsers.py
├── profiles.py
├── proxy_pool.py
└── py.typed

tests/
├── conftest.py
├── test_config.py
├── test_models.py
├── test_public_api.py
├── test_humanizer.py
├── test_humanizer_properties.py   # Hypothesis property tests
├── test_humanizer_activity.py
├── test_foxcape.py                # mocked Camoufox sync
├── test_async_foxcape.py          # mocked AsyncCamoufox
├── test_parsers.py
├── test_proxy_pool.py
├── test_profiles.py
├── test_cadence.py
├── test_scrape_cadence.py
├── test_camoufox_launch.py
├── test_evasion_scripts.py
├── test_turnstile_and_typing.py
├── test_smoke_contract.py
├── test_edge_cases.py
└── test_integration.py            # @pytest.mark.live

.github/workflows/
├── ci.yml                   # DONE
├── publish.yml              # DONE (Trusted Publisher pending T026)
└── sonarqube.yml            # DONE
```

**Structure Decision**: Single-package `src/` layout per hatchling; tests at repo root `tests/`; SpecKit artifacts under `specs/001-initial-release/`.

## Complexity Tracking

No constitution violations requiring justification.
