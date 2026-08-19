# Tasks: Foxcape Initial Release (v0.1.0)

**Input**: Design documents from `/specs/001-initial-release/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/public-api.md, quickstart.md

**Tests**: Included per spec FR-010 and constitution II (offline CI).

**Organization**: By user story; bootstrap/migration phases marked complete.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup (Shared Infrastructure) — COMPLETE

- [x] T001 Create pyproject.toml, uv.lock, LICENSE, .gitignore at repo root
- [x] T002 [P] Configure hatchling src layout and `src/foxcape/py.typed`
- [x] T003 [P] Initialize `.specify/` and `specs/001-initial-release/`
- [x] T004 Configure pre-commit, ruff, mypy, pytest markers in pyproject.toml
- [x] T005 Git init, remote origin, Gitflow branches (`develop`, `main`)
- [x] T006 Create Makefile quality gates (`install`, `lint`, `typecheck`, `test`, `check`)
- [x] T007 Create `.github/workflows/ci.yml` matrix py3.10–3.13 ubuntu

---

## Phase 2: Foundational (Blocking Prerequisites) — COMPLETE

- [x] T008 Migrate all modules to `src/foxcape/` with Foxcape renames
- [x] T009 Create `src/foxcape/exceptions.py` (FoxcapeError, BrowserStartupError)
- [x] T010 Assemble `src/foxcape/__init__.py` with stable `__all__` and `__version__ = "0.1.0"`
- [x] T011 [P] Add baseline offline tests: `tests/conftest.py`, `test_config.py`, `test_models.py`, `test_public_api.py`
- [x] T012 Ratify constitution in `.specify/memory/constitution.md`

**Checkpoint**: Foundation ready — user story hardening can proceed.

---

## Phase 3: User Story 1 — Install and scrape (P1)

**Goal**: pip install + sync scrape with clear Camoufox-missing error.

**Independent Test**: Mocked `Foxcape.get` returns FoxcapeResult; import has no side effects.

### Tests

- [ ] T013 [P] [US1] Add `tests/test_foxcape.py` mocking `camoufox.sync_api.Camoufox` — lifecycle + get()
- [ ] T014 [P] [US1] Add import side-effect test in `tests/test_public_api.py` (no browser on import)

### Implementation

- [ ] T015 [US1] Verify clear `BrowserStartupError` when Camoufox unavailable in `src/foxcape/scraper.py`
- [ ] T016 [US1] Align README quickstart with spec Scenario 1 in `README.md`

**Checkpoint**: US1 independently testable offline.

---

## Phase 4: User Story 2 — Async scraping (P1)

**Goal**: AsyncFoxcape parity with sync; cleanup on error.

**Independent Test**: Mocked async context manager and `afetch`.

### Tests

- [ ] T017 [P] [US2] Add `tests/test_async_foxcape.py` mocking `camoufox.async_api.AsyncCamoufox`
- [ ] T018 [P] [US2] Test async context manager closes browser on exception

### Implementation

- [ ] T019 [US2] Verify `BrowserStartupError` paths in `src/foxcape/async_scraper.py`

**Checkpoint**: US1 + US2 offline green.

---

## Phase 5: User Story 3 — Proxies and profiles (P2)

**Goal**: ProxyConfig, pool sticky sessions, profile warmup config export.

**Independent Test**: Existing pool tests + profile `to_foxcape_config` unit test.

### Tests

- [ ] T020 [P] [US3] Add `tests/test_profiles.py` for metadata, `to_foxcape_config`, lock cleanup (mock Foxcape in warmup)
- [ ] T021 [P] [US3] Extend proxy pool edge case: empty pool returns None

### Implementation

- [ ] T022 [US3] Document proxy/profile usage in `README.md` (from quickstart Scenarios 3 & 5)

**Checkpoint**: US3 testable without live browser (warmup mocked).

---

## Phase 6: User Story 4 — LLM extraction (P2)

**Goal**: Clean text, markdown, links helpers validated.

**Independent Test**: `test_models.py` + humanizer path test.

### Tests

- [ ] T023 [P] [US4] Add `tests/test_humanizer.py` for `generate_windmouse_path` length/endpoint/delay
- [ ] T024 [P] [US4] Add parser edge cases in `tests/test_models.py` (empty HTML, relative links)

**Checkpoint**: US4 fully offline.

---

## Phase 7: User Story 5 — CI and PyPI (P2)

**Goal**: Publish workflow + trusted publisher + release tag.

**Independent Test**: CI green on PR; publish workflow dry-run or staging.

### Implementation

- [ ] T025 [P] [US5] Create `.github/workflows/publish.yml` (tag v*, uv build, pypa/gh-action-pypi-publish OIDC)
- [ ] T026 [US5] Configure PyPI Trusted Publisher for `andreferraro/foxcape` workflow `publish.yml`
- [ ] T027 [P] [US5] Add `tests/test_integration.py` with `@pytest.mark.live` (example.com sync+async)
- [ ] T028 [US5] Gitflow release: branch `release/v0.1.0`, merge to `main`, tag `v0.1.0`, merge back to `develop`

**Checkpoint**: v0.1.0 publishable.

---

## Phase 8: Polish & Converge

- [ ] T029 [P] Run `/speckit-converge` and produce `specs/001-initial-release/test-evidence.json`
- [ ] T030 [P] Mark completed items in `checklists/release-gate.md`
- [ ] T031 Update `docs/PLAN.md` phase status to reflect v0.1.0 ship

---

## Dependencies & Execution Order

```text
Phase 1–2 (done) → US1 (T013–T016) → US2 (T017–T019) [parallel after mocks pattern]
                → US3, US4 [parallel]
                → US5 (publish, depends on offline tests green)
                → Converge
```

### Parallel opportunities

- T013, T014, T017, T018, T020, T021, T023, T024 can run in parallel once mock pattern established in T013.
- T025, T027 parallel while US1–4 tests land.

## Implementation strategy

1. **MVP**: Complete US1 mocks (T013–T016) → first offline proof of scrape path.
2. Add US2 async mocks.
3. Fill US3–US4 test gaps.
4. US5 publish + tag only when `make check` green on all matrix Python versions.
5. `/speckit-implement` executes remaining unchecked tasks only.

---

## Notes

- Do **not** start `/speckit-implement` until `/speckit-analyze` gate passes.
- Tasks T001–T012 already completed in bootstrap/migration commits.
