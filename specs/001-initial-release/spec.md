# Feature Specification: Foxcape Initial Release (v0.1.0)

**Feature Branch**: `001-initial-release`

**Created**: 2026-08-19

**Status**: Draft

**Input**: Publish Foxcape as an installable Python library for undetectable web scraping — sync/async API, proxy & profile support, LLM-friendly extraction, offline CI, and PyPI release v0.1.0. Source: `docs/PLAN.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and scrape (Priority: P1)

A Python developer installs Foxcape from PyPI, prepares the stealth browser once, and fetches a page with minimal boilerplate.

**Why this priority**: Core value proposition — without install + scrape, nothing else matters.

**Independent Test**: `pip install foxcape`, run one sync scrape script against a public URL; verify title and HTML are returned.

**Acceptance Scenarios**:

1. **Given** a clean Python 3.10+ environment, **When** the developer runs `pip install foxcape` and `import foxcape`, **Then** import succeeds with no side effects (no browser launch, no network).
2. **Given** Camoufox browser binaries are fetched, **When** the developer uses `Foxcape` context manager with `get(url)`, **Then** a structured result with title, HTML, and status code is returned.
3. **Given** Camoufox is not installed, **When** the developer starts `Foxcape`, **Then** a clear error explains how to run `python -m camoufox fetch`.

---

### User Story 2 - Async scraping (Priority: P1)

A developer building asyncio pipelines uses `AsyncFoxcape` with the same capabilities as sync.

**Why this priority**: Async is a first-class use case for modern scrapers and must ship in v0.1.0.

**Independent Test**: Async context manager fetches a page; `afetch` one-liner works; browser closes on exception.

**Acceptance Scenarios**:

1. **Given** an async event loop, **When** `async with AsyncFoxcape()` and `await fox.get(url)`, **Then** result parity with sync (title, HTML, status).
2. **Given** an error mid-request, **When** the async context exits, **Then** browser resources are released.
3. **Given** default config, **When** `AsyncFoxcape.afetch(url)` is called, **Then** a complete result is returned without manual lifecycle management.

---

### User Story 3 - Proxies and browser profiles (Priority: P2)

A developer routes traffic through proxies and reuses warmed browser profiles for higher trust scores.

**Why this priority**: Production scraping requires proxy rotation and session persistence.

**Independent Test**: Configure proxy URL; create profile, run warmup, scrape with profile-derived config; sticky proxy session returns same endpoint.

**Acceptance Scenarios**:

1. **Given** a proxy URL string, **When** passed to `FoxcapeConfig`, **Then** requests route through that proxy.
2. **Given** a new profile name, **When** `ProfileManager.get_or_create` and optional `warmup`, **Then** profile metadata records warmth and visited domains.
3. **Given** a proxy pool with multiple endpoints, **When** `get_proxy(session_id=...)` is called twice with the same id, **Then** the same proxy is returned (sticky session).

---

### User Story 4 - LLM-friendly content extraction (Priority: P2)

A developer feeding pages to an LLM needs clean text, markdown summaries, and structured links without scripts or boilerplate.

**Why this priority**: Differentiator for AI pipelines — raw HTML is insufficient.

**Independent Test**: Parse sample HTML offline; clean text excludes script content; markdown contains headings; links list is structured.

**Acceptance Scenarios**:

1. **Given** HTML with scripts and navigation chrome, **When** `get_clean_text()` is called, **Then** readable body text is returned without script bodies.
2. **Given** parsed page, **When** `to_markdown()` is called, **Then** hierarchical markdown suitable for LLM context is produced.
3. **Given** a page with anchors, **When** `extract_links()` is called, **Then** a list of link records with resolved URLs is returned.

---

### User Story 5 - Quality gates and PyPI publish (Priority: P2)

Maintainers merge only when offline CI passes; v0.1.0 is published to PyPI via trusted publishing.

**Why this priority**: Public library requires reproducible quality and a trustworthy release path.

**Independent Test**: CI matrix passes without network; tagging triggers publish workflow (staging validation).

**Acceptance Scenarios**:

1. **Given** a pull request to `develop`, **When** CI runs, **Then** ruff, mypy, and offline pytest pass on Ubuntu × Python 3.10–3.13 without downloading Camoufox.
2. **Given** a semver tag `v0.1.0` on `main`, **When** publish workflow runs, **Then** a wheel is uploaded to PyPI via OIDC (no long-lived tokens in repo).
3. **Given** default pytest invocation, **When** tests run, **Then** `@pytest.mark.live` tests are excluded.

---

### Edge Cases

- Camoufox browser binaries missing → actionable startup error, not opaque stack trace.
- Parser engine `lxml` unavailable → fallback or clear error (constitution: lxml is a declared dependency).
- Stale `parent.lock` on profile directory → profile cleanup removes lock before use.
- Empty proxy pool → `get_proxy` returns `None` without crashing.
- Partial warmup failure → profile still usable; failed URLs logged, warmth may be partial.
- Cloudflare Turnstile present → optional auto-solve when enabled in config.
- Importing package must never launch browser or open network connections.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Package MUST be installable from PyPI as `foxcape` with Python `>=3.10,<4.0`.
- **FR-002**: Public API MUST be defined exclusively via `foxcape.__all__` (stable semver from 0.1.0).
- **FR-003**: Sync scraper MUST support context-manager lifecycle (`Foxcape`) with `get`, `fetch`, `type_human`, and `evaluate`.
- **FR-004**: Async scraper MUST support async context manager (`AsyncFoxcape`) with parity to sync including `afetch`.
- **FR-005**: Configuration MUST be expressible via `FoxcapeConfig` dataclass with documented defaults.
- **FR-006**: Results MUST expose parsing helpers: `select`, `select_one`, `get_clean_text`, `to_markdown`, `extract_links`.
- **FR-007**: Proxy support MUST accept URL strings, `ProxyConfig`, or Playwright-compatible dicts; pool MUST support round-robin and sticky sessions.
- **FR-008**: Browser profiles MUST persist metadata, support warmup categories, and convert to `FoxcapeConfig`.
- **FR-009**: Library MUST expose minimal exceptions (`FoxcapeError`, `BrowserStartupError`); Playwright types MUST NOT appear in public API.
- **FR-010**: Default CI MUST run offline tests only; live browser tests MUST be opt-in via marker.
- **FR-011**: README MUST include install steps, quickstart examples, and responsible-use disclaimer.
- **FR-012**: Repository MUST follow Gitflow with `develop` as default integration branch.

### Key Entities

- **FoxcapeConfig**: User-facing scrape settings (headless, humanize, proxy, timeouts, noise flags, profile paths).
- **FoxcapeResult**: Scrape output (url, html, soup, status_code, title) plus extraction helpers.
- **Foxcape / AsyncFoxcape**: Session-scoped browser facade (sync vs async).
- **ProxyConfig**: Proxy endpoint credentials for Camoufox/Playwright.
- **ProxyPoolManager**: Collection of proxies with selection strategies.
- **BrowserProfile**: Named persistent profile with warmth metadata and warmup history.
- **ProfileManager**: Factory for creating/listing profiles on disk.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new developer can install, configure, and fetch a page in under 15 minutes following README quickstart (excluding one-time Camoufox download).
- **SC-002**: 100% of default CI jobs pass on merge without network access or browser binaries.
- **SC-003**: Public API surface matches `__all__` — every export importable, no undocumented public symbols.
- **SC-004**: Offline test suite covers config defaults, result parsing, public exports, and mocked browser lifecycle before v0.1.0 tag.
- **SC-005**: v0.1.0 wheel installs via `pip install foxcape` and passes smoke import on Python 3.10 and 3.13.

## Assumptions

- Target users are Python developers familiar with `pip` and virtual environments.
- Camoufox is the sole browser engine; users accept one-time `camoufox fetch` for local/live use.
- v0.1.0 targets Ubuntu CI only; macOS/Windows browser CI is out of scope.
- Stealth/evasion features are used responsibly; legal/ToS compliance is the consumer's responsibility.
- Bootstrap (src layout, git remote, baseline tests) is complete; remaining work is mocks, publish workflow, and release.

## Clarifications

### Session 2026-08-19

- Q: Scope of v0.1.0? → A: Full PLAN.md scope — all five user stories, offline CI, PyPI 0.1.0, no stealth_scraper compatibility aliases.
- Q: Implementation before analyze gate? → A: Bootstrap/migration allowed; feature completion follows `/speckit-analyze` approval.
- Q: Live integration tests in CI? → A: Excluded; `@pytest.mark.live` only for manual/optional runs.
