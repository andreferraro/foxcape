# Interface Contract: Foxcape HTML Cleaner

**Feature**: Optional HTML Cleaner (`specs/002-html-cleaner/spec.md`)
**Status**: Final
**Date**: 2026-08-21

---

## 1. Standalone Function Contract

```python
def clean_html(
    html: str,
    parser_engine: Literal["lxml", "html.parser"] = "lxml",
    rules: CleanerRules | None = None,
) -> str:
    """Cleans rendered HTML markup by removing advertising, widgets, CMP banners, and overlays.

    Args:
        html: Raw HTML string to be cleaned.
        parser_engine: BeautifulSoup parser backend ("lxml" or "html.parser"). Defaults to "lxml".
        rules: Optional custom CleanerRules instance. Defaults to DEFAULT_RULES.

    Returns:
        Cleaned, serialized HTML string. If parsing fails, returns the original input string.
    """
```

---

## 2. Cleaner Engine Class Contract

```python
class HTMLCleaner:
    """Modular DOM cleaning engine applying rule-based sanitization passes."""

    def __init__(
        self,
        parser_engine: Literal["lxml", "html.parser"] = "lxml",
        rules: CleanerRules | None = None,
    ) -> None:
        self.parser_engine = parser_engine
        self.rules = rules or DEFAULT_RULES

    def clean(self, html: str) -> str:
        """Executes full cleaning pipeline on an HTML string."""
        ...

    def clean_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Applies sanitization rules in-place to an existing BeautifulSoup tree."""
        ...
```

---

## 3. Scraper Entry Points Contract

### 3.1 `FoxcapeConfig`
```python
@dataclass
class FoxcapeConfig:
    # Existing fields...
    clean_html: bool = False
```

### 3.2 `Foxcape` (Synchronous)
```python
class Foxcape:
    def get(
        self,
        url: str,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
        clean_html: bool | None = None,
    ) -> FoxcapeResult: ...

    @classmethod
    def fetch(
        cls,
        url: str,
        config: FoxcapeConfig | None = None,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
        clean_html: bool | None = None,
    ) -> FoxcapeResult: ...
```

### 3.3 `AsyncFoxcape` (Asynchronous)
```python
class AsyncFoxcape:
    async def get(
        self,
        url: str,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
        clean_html: bool | None = None,
    ) -> FoxcapeResult: ...

    @classmethod
    async def afetch(
        cls,
        url: str,
        config: FoxcapeConfig | None = None,
        wait_selector: str | None = None,
        wait_until: str | None = None,
        timeout_ms: int | None = None,
        simulate_mouse: bool | None = None,
        solve_turnstile: bool | None = None,
        human_delay: bool = True,
        clean_html: bool | None = None,
    ) -> FoxcapeResult: ...
```
