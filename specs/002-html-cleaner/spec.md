# Feature Specification: Optional HTML Cleaner

**Feature Branch**: `002-html-cleaner`

**Created**: 2026-08-21

**Status**: Draft

**Input**: Add an optional HTML cleaning feature to Foxcape: when enabled, remove advertising, recommendation widgets, LGPD/consent banners, and suspicious overlays from the rendered HTML before it is returned; when absent, behavior is unchanged. Source: `docs/PRD_cleaner.md`.

## Clarifications

### Session 2026-08-21

- Q: Como o parâmetro `clean_html` deve ser exposto na API pública do Foxcape? → A: Suportar tanto em `FoxcapeConfig(clean_html: bool = False)` quanto como override pontual em `.get(clean_html=...)`, `.fetch(clean_html=...)` e métodos assíncronos correspondentes (`AsyncFoxcape`).
- Q: A função de limpeza deve ser exposta diretamente no módulo principal (`foxcape`) como uma função utilitária independente em `__all__`? → A: Sim, seguir o padrão do projeto exportando `clean_html(html: str) -> str` diretamente no `foxcape.__all__` para processamento standalone.
- Q: Como a detecção de overlays deve ser realizada pelo cleaner? → A: Processamento puramente estático da DOM via BeautifulSoup/lxml (inspecionando tags, atributos `style` como `position: fixed`/`z-index`/dimensões inline e classes/IDs suspeitos), garantindo operação offline sem requerer injeção JS no navegador.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cleaned HTML on demand (Priority: P1)

A developer scraping content-heavy pages enables cleaning and receives the rendered HTML free of ads, recommendation widgets, consent banners, and overlay pollution.

**Why this priority**: This is the core value proposition — the cleaner exists to deliver cleaner HTML without changing anything else.

**Independent Test**: Enable cleaning on a fixture page containing ads, widgets, and a consent banner; verify those elements are absent from the returned HTML.

**Acceptance Scenarios**:

1. **Given** a page containing advertising, recommendation widgets, a consent banner, and an overlay, **When** cleaning is enabled, **Then** all such elements are removed from the returned HTML.
2. **Given** a page with no removable elements, **When** cleaning is enabled, **Then** the returned HTML retains all content (no false removals).
3. **Given** the cleaner is enabled, **When** the result is returned, **Then** the HTML is valid, serialized markup usable by existing extraction helpers.

---

### User Story 2 - Unchanged behavior when disabled (Priority: P1)

A developer using Foxcape today gets byte-for-byte the same behavior when the cleaning option is not used.

**Why this priority**: Backward compatibility is the safety guarantee — the feature must be invisible unless opted in.

**Independent Test**: Run existing scraping flows without the option and confirm the returned HTML matches pre-feature output.

**Acceptance Scenarios**:

1. **Given** the cleaning option is absent or disabled, **When** any page is scraped, **Then** no cleaning processing runs and the returned HTML is unchanged.
2. **Given** the cleaning option is absent, **When** the page contains ads or banners, **Then** they remain in the HTML exactly as before.

---

### User Story 3 - Conservative overlay handling (Priority: P2)

A developer benefits from overlay removal that never sacrifices the page's main content.

**Why this priority**: Overlay removal carries the highest false-positive risk and must err on the side of preserving content.

**Independent Test**: Feed a page with a full-screen dialog and a normal fixed header; verify only the overlay is removed.

**Acceptance Scenarios**:

1. **Given** an overlay occupying most of the viewport with fixed positioning and high stacking, **When** cleaning runs, **Then** the overlay is removed.
2. **Given** an element merely named `modal` or `popup` without the overlay characteristics, **When** cleaning runs, **Then** the element is NOT removed.
3. **Given** main article content inside or below a suspected overlay, **When** cleaning runs, **Then** the main content is preserved.

---

### User Story 4 - Maintainable rules catalog (Priority: P3)

A maintainer extends or corrects what the cleaner removes without touching the cleaning engine.

**Why this priority**: Fingerprints drift as ad networks evolve; separation keeps the feature sustainable.

**Independent Test**: Add a new fingerprint to the rules catalog; confirm the cleaner picks it up with no engine change.

**Acceptance Scenarios**:

1. **Given** the rules catalog, **When** a new fingerprint is added, **Then** the cleaner applies it on the next run.
2. **Given** the rules catalog, **When** a fingerprint is removed, **Then** the cleaner stops removing matching elements.

---

### Edge Cases

- What happens when the HTML contains malformed markup that cannot be parsed? The cleaner must degrade gracefully and return the input unchanged rather than fail.
- How does the cleaner handle elements nested inside one another (e.g., an ad inside a consent banner)? Each rule must apply cleanly without corrupting the document.
- What if a suspected overlay contains legitimate content? Conservative criteria require multiple signals before removal, and the element name alone is never sufficient.
- What happens when scripts or iframes match ad fingerprints but carry no advertising? Fingerprint-based removal is accepted as the rule; no semantic verification is performed.
- Does serialization alter the original document? The cleaner returns a re-serialized HTML; formatting normalization is accepted when cleaning is enabled.
- What about pages with no removable elements at all? The cleaner must be a no-op for content (no false positives), only serializing the document.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an optional `clean_html: bool = False` parameter in `FoxcapeConfig` and allow per-call override (`clean_html: bool | None = None`) in `Foxcape.get()`, `Foxcape.fetch()`, and async equivalents (`AsyncFoxcape.get()`, `AsyncFoxcape.fetch()`); when absent or False, NO cleaning processing runs and returned HTML is identical to current behavior.
- **FR-002**: When enabled, the system MUST apply the cleaner to the fully rendered HTML (after page JavaScript and DOM generation) before returning the result.
- **FR-003**: System MUST remove Google AdSense elements identified by known fingerprints (e.g., `adsbygoogle`, `google-auto-placed`, `google_ads`, `ad-container`, `ad-slot`).
- **FR-004**: System MUST remove scripts referencing ad networks (`adsbygoogle.js`, `googlesyndication`, `doubleclick.net`).
- **FR-005**: System MUST remove iframes referencing ad networks (`googleads`, `doubleclick`, `googlesyndication`).
- **FR-006**: System MUST remove Outbrain recommendation widgets and scripts.
- **FR-007**: System MUST remove Taboola recommendation widgets and scripts.
- **FR-008**: System MUST remove RevContent recommendation widgets and scripts.
- **FR-009**: System MUST remove consent banners and CMP components (cookie/consent/GDPR/LGPD/privacy markers and known providers such as OneTrust, Cookiebot, Quantcast).
- **FR-010**: System MUST remove overlays via static DOM inspection ONLY when multiple characteristics combine (e.g. inline `style` with fixed/absolute positioning, high `z-index`, large viewport dimensions, combined with suspicious overlay/modal/backdrop class or ID names); removal on a single characteristic — including a suspicious class or ID name alone — is FORBIDDEN.
- **FR-011**: System MUST preserve main content; no element may be removed on an isolated heuristic alone.
- **FR-012**: System MUST keep cleaning rules separate from the cleaning engine, so fingerprints can be maintained independently.
- **FR-013**: System MUST apply the cleaner consistently across all scraping entry points (sync and async `Foxcape` / `AsyncFoxcape`) respecting both instance-level `FoxcapeConfig.clean_html` and call-level overrides.
- **FR-014**: System MUST implement cleaning using the project's existing dependencies only; NO new third-party library is added.
- **FR-015**: System MUST NOT use machine learning, LLM-based classification, browser-level request blocking, AdBlock filter lists, or any change to Camoufox behavior.
- **FR-016**: When the enabled cleaner produces invalid or unparseable HTML, the system MUST fall back to returning the original input rather than raising an error.
- **FR-017**: System MUST export `clean_html(html: str, parser_engine: str = "lxml") -> str` in `foxcape.__all__` for standalone offline HTML cleaning without requiring browser initialization.

### Key Entities *(include if feature involves data)*

- **Cleaned HTML**: The serialized HTML output returned to the caller when the option is enabled; used by downstream extraction and processing.
- **Cleaning Rules**: The catalog of fingerprints (class/ID/attribute markers, script and iframe patterns) that determines which elements are removable.
- **Rendered HTML (input)**: The fully rendered page HTML captured after DOM readiness; the input to the cleaning pipeline.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the option disabled, 100% of existing behavior and output is preserved (existing tests pass unchanged).
- **SC-002**: With the option enabled, 100% of tested fixture elements matching known ad, widget, and consent fingerprints are removed from the returned HTML.
- **SC-003**: Zero false removals of main content across the fixture corpus (overlay rule never removes content based on a single heuristic).
- **SC-004**: The cleaning pipeline completes without network access, LLM calls, or new dependencies — fully exercisable in deterministic offline CI.
- **SC-005**: Cleaning adds no perceptible end-to-end latency to scraping (cleaner completes within standard page-processing time without blocking the result).
- **SC-006**: The rules catalog is editable independently of the engine, and a rule change takes effect without engine modification.

## Assumptions

- The cleaning option follows the existing Foxcape configuration pattern: a config default that can be overridden per call (mirroring existing optional behavior flags).
- The option applies uniformly to sync and async entry points when set at the config level.
- Fingerprint-based removal is accepted as the rule; no semantic verification is performed on matched elements.
- Re-serialization may normalize HTML formatting when cleaning is enabled; byte-identical formatting is only guaranteed when the option is disabled.
- Overlay removal thresholds (roughly 70%+ viewport width, 30%+ viewport height, fixed positioning, high stacking order) are the initial conservative criteria and may be tuned within the rules catalog.
- Removing an element removes its entire subtree (descendants included).
- Empty wrapper containers left behind after removal may remain; cleanup of empty wrappers is out of scope.
- No new runtime dependency is introduced; the project constitution's dependency boundary is respected.
