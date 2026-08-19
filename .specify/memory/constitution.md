# Foxcape Library Constitution

## I. Public Library Boundary

Zero coupling to consumer apps. Runtime deps: camoufox[geoip], beautifulsoup4, lxml only.

## II. Deterministic Offline CI

pytest -m "not live" blocks merge. No network, no camoufox fetch in default CI.

## III. Camoufox-Only Engine

Playwright not in public API (`__all__`). Internal use only.

## IV. Ponytail / YAGNI

No mypy strict, no full Playwright exception wrap, no multi-OS browser CI v1.

## V. Stable Public API

`__all__` defines public surface. Semver from 0.1.0.

---

**Version:** 1.0.0 | **Ratified:** 2026-08-19
