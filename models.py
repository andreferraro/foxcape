from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

from .parsers import build_soup, dom_to_markdown_summary, extract_clean_text, extract_links_from_soup


@dataclass
class ScrapeResult:
    """Encapsulates raw scrape response and provides deterministic and AI-friendly DOM helpers."""

    url: str
    html: str
    soup: BeautifulSoup
    status_code: int | None = None
    title: str = ""

    @classmethod
    def from_html(
        cls,
        html: str,
        url: str = "",
        status_code: int | None = None,
        parser_engine: str = "lxml",
    ) -> "ScrapeResult":
        soup = build_soup(html, parser_engine)
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        return cls(url=url, html=html, soup=soup, status_code=status_code, title=title)

    def select_one(self, selector: str) -> Tag | None:
        """Deterministic CSS selector single match."""
        return self.soup.select_one(selector)

    def select(self, selector: str) -> list[Tag]:
        """Deterministic CSS selector multi match."""
        return self.soup.select(selector)

    def get_clean_text(self) -> str:
        """Strip boilerplate/scripts and return clean readable text."""
        return extract_clean_text(self.soup)

    def extract_links(self) -> list[dict]:
        """Extract structured list of links with resolved full URLs."""
        return extract_links_from_soup(self.soup, base_url=self.url)

    def to_markdown(self) -> str:
        """Convert page hierarchy into clean markdown format suitable for LLMs."""
        return dom_to_markdown_summary(self.soup)
