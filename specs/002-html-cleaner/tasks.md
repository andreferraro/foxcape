# Implementation Tasks: Optional HTML Cleaner

**Feature**: Optional HTML Cleaner (`specs/002-html-cleaner/spec.md`)  
**Branch**: `002-html-cleaner` | **Date**: 2026-08-21  
**Status**: Ready for Implementation  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize directory structure and static test fixtures for offline validation.

- [X] T001 Create cleaner module directory at `src/foxcape/cleaner/` and fixtures directory at `tests/fixtures/cleaner/`
- [X] T002 [P] Create offline HTML fixtures (`adsense.html`, `taboola_outbrain.html`, `cmp_consent.html`, `overlay.html`, `clean_page.html`) in `tests/fixtures/cleaner/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core rule definitions, engine boilerplate, and configuration fields that MUST be complete before user stories can be integrated.

- [X] T003 Define fingerprint patterns and compile-ready selectors for AdSense, Outbrain, Taboola, RevContent, CMPs, and Overlays in `src/foxcape/cleaner/rules.py`
- [X] T004 Implement core DOM parsing, tree decomposition helpers, and fallback error handling in `src/foxcape/cleaner/cleaner.py`
- [X] T005 [P] Expose `HTMLCleaner` and standalone `clean_html()` in `src/foxcape/cleaner/__init__.py`
- [X] T006 Add `clean_html: bool = False` configuration field to `FoxcapeConfig` in `src/foxcape/config.py`

**Checkpoint**: Foundation ready - rules and cleaner engine skeleton are available for user story implementation.

---

## Phase 3: User Story 1 - Cleaned HTML on demand (Priority: P1) 🚀 MVP

**Goal**: When `clean_html=True` is configured or passed as a per-call override, Foxcape parses the rendered HTML and strips ads, widgets, and consent banners before returning `FoxcapeResult`. Also export standalone `clean_html()` in `foxcape.__all__`.

**Independent Test**: Feed fixture HTML with ads/widgets to `clean_html()` or `Foxcape.get(..., clean_html=True)` and verify returned markup contains no ad/widget/consent nodes while preserving article content.

### Tests for User Story 1
- [X] T007 [P] [US1] Create unit tests for standalone `clean_html()` and individual rule passes in `tests/test_cleaner.py`
- [X] T008 [P] [US1] Create integration tests verifying `Foxcape.get()` and `AsyncFoxcape.get()` return cleaned HTML when `clean_html=True` in `tests/test_cleaner.py`

### Implementation for User Story 1
- [X] T009 [US1] Implement 8-stage cleaning pipeline in `HTMLCleaner.clean()` and `clean_html()` in `src/foxcape/cleaner/cleaner.py`
- [X] T010 [US1] Export `clean_html` in `src/foxcape/__init__.py` and add to `__all__`
- [X] T011 [US1] Integrate `clean_html` parameter and per-call override logic in `Foxcape.get()` and `Foxcape.fetch()` in `src/foxcape/scraper.py`
- [X] T012 [US1] Integrate `clean_html` parameter and per-call override logic in `AsyncFoxcape.get()` and `AsyncFoxcape.fetch()` in `src/foxcape/async_scraper.py`

**Checkpoint**: User Story 1 complete — HTML cleaning works on demand via standalone function and scraper instances.

---

## Phase 4: User Story 2 - Unchanged behavior when disabled (Priority: P1)

**Goal**: When `clean_html` is absent or `False`, Foxcape bypasses the cleaner completely, returning byte-identical HTML with zero overhead.

**Independent Test**: Execute `Foxcape.get()` and `AsyncFoxcape.get()` without `clean_html` on ad-laden pages and verify output exactly matches unmodified input markup.

### Tests for User Story 2
- [X] T013 [P] [US2] Create regression tests in `tests/test_cleaner.py` asserting byte-identical raw output when `clean_html=False` or omitted

### Implementation for User Story 2
- [X] T014 [US2] Ensure scraper directly forwards `page.content()` without initializing BeautifulSoup or `HTMLCleaner` when `clean_html` evaluates to `False` in `src/foxcape/scraper.py` and `src/foxcape/async_scraper.py`

**Checkpoint**: User Stories 1 and 2 functional — cleaning is opt-in and backward-compatible.

---

## Phase 5: User Story 3 - Conservative overlay handling (Priority: P2)

**Goal**: Remove intrusive full-screen fixed overlays while guaranteeing that normal modals, headers, or article text are never removed on a single heuristic.

**Independent Test**: Pass HTML containing a full-screen overlay backdrop and a legitimate modal/header to `clean_html()`; verify only the intrusive fixed overlay is stripped.

### Tests for User Story 3
- [X] T015 [P] [US3] Create unit tests in `tests/test_cleaner.py` for multi-criteria overlay detection and false-positive prevention

### Implementation for User Story 3
- [X] T016 [US3] Implement static multi-criteria overlay inspection (`position: fixed`/`absolute`, high `z-index`, large viewport style properties combined with overlay markers) in `src/foxcape/cleaner/cleaner.py`

**Checkpoint**: User Story 3 complete — overlay filtering is conservative and safe.

---

## Phase 6: User Story 4 - Maintainable rules catalog (Priority: P3)

**Goal**: Ensure ad and CMP fingerprints can be updated or extended in `rules.py` without requiring engine changes in `cleaner.py`.

**Independent Test**: Programmatically register a custom fingerprint in `rules.py` and confirm `HTMLCleaner` detects and removes matching elements without engine edits.

### Tests for User Story 4
- [X] T017 [P] [US4] Create unit test in `tests/test_cleaner.py` verifying rule extensibility from `rules.py`

### Implementation for User Story 4
- [X] T018 [US4] Structure `src/foxcape/cleaner/rules.py` into clear immutable sets and dataclasses with extension documentation

**Checkpoint**: All user stories complete and independently tested.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verification, linting, type-safety, and quickstart scenario validation.

- [X] T019 [P] Run full offline test suite (`pytest -m "not live"`) and verify 100% pass rate
- [X] T020 [P] Run code quality and type checks (`ruff check`, `mypy`) on `src/foxcape/cleaner/` and modified scraper files
- [X] T021 Validate all end-to-end scenarios documented in `specs/002-html-cleaner/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 (T001-T002) — BLOCKS all user story tasks.
- **User Story 1 (Phase 3)**: Depends on Phase 2 (T003-T006). Delivers MVP.
- **User Story 2 (Phase 4)**: Depends on Phase 2 & T011/T012.
- **User Story 3 (Phase 5)**: Depends on Phase 2 & T009.
- **User Story 4 (Phase 6)**: Depends on Phase 2 (T003).
- **Polish (Phase 7)**: Depends on completion of all user stories.

### Parallel Opportunities

- `T002` (fixtures) can be created in parallel with `T001`.
- `T005` (`__init__.py`) and `T006` (`config.py`) can run in parallel.
- `T007` and `T008` (tests for US1) can be authored in parallel before implementation.
- `T013` (US2 tests), `T015` (US3 tests), and `T017` (US4 tests) can run in parallel.
- `T019` (pytest) and `T020` (ruff/mypy) can run in parallel during Phase 7.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete **Phase 1: Setup** (T001 - T002).
2. Complete **Phase 2: Foundational** (T003 - T006).
3. Complete **Phase 3: User Story 1** (T007 - T012).
4. Run `pytest tests/test_cleaner.py` to validate MVP independently.

### Incremental Delivery
1. Add User Story 2 (Zero overhead when disabled) → Validate backward compatibility.
2. Add User Story 3 (Conservative overlay removal) → Validate false-positive safety.
3. Add User Story 4 (Rules catalog maintainability) → Validate extensibility.
4. Run Polish (Phase 7) → Final CI check.
