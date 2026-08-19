# Release Gate Checklist: Foxcape v0.1.0

**Purpose**: Requirements-quality validation before `/speckit-implement` and release  
**Created**: 2026-08-19  
**Feature**: [spec.md](../spec.md)

## Public API requirements

- [ ] Does the spec define every symbol in `contracts/public-api.md` with testable behavior?
- [ ] Are sync/async parity requirements explicit for `get` vs `afetch`?
- [ ] Is the "no import side effects" requirement stated and testable?

## Offline CI requirements

- [ ] Does the spec state that default CI excludes network and Camoufox fetch?
- [ ] Are live tests explicitly marked and excluded from merge gates?
- [ ] Is the mock strategy for Camoufox documented in plan/tasks?

## Publishing requirements

- [ ] Is PyPI trusted publishing (OIDC) specified without long-lived tokens?
- [ ] Is semver 0.1.0 tag workflow defined?
- [ ] Is Gitflow merge path (develop → release → main) documented?

## Responsible use & docs

- [ ] Is the responsible-use disclaimer required in README?
- [ ] Do quickstart scenarios map to each P1/P2 user story?

## Constitution alignment

- [ ] Public library boundary (runtime deps only) reflected in requirements?
- [ ] Playwright excluded from public API in contract?
- [ ] YAGNI constraints (no strict mypy, no multi-OS browser CI) honored?

## Notes

- Reviewer marks `[x]` when the requirement writing criterion is satisfied.
- All items should pass before `/speckit-implement`.
