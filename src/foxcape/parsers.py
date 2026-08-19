import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def build_soup(html: str, parser_engine: str = "lxml") -> BeautifulSoup:
    """Build BeautifulSoup instance with graceful fallback."""
    try:
        return BeautifulSoup(html, parser_engine)
    except Exception:
        return BeautifulSoup(html, "html.parser")


def extract_clean_text(soup: BeautifulSoup) -> str:
    """Extract clean readable text from DOM, stripping noise tags."""
    soup_copy = BeautifulSoup(str(soup), "html.parser")
    for tag in soup_copy(["script", "style", "noscript", "svg", "header", "footer"]):
        tag.decompose()
    text = soup_copy.get_text(separator="\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text)


def extract_links_from_soup(soup: BeautifulSoup, base_url: str = "") -> list[dict]:
    """Extract structured hyperlinks from BeautifulSoup tree."""
    links = []
    for a in soup.find_all("a", href=True):
        raw_href = a.get("href")
        if not raw_href:
            continue
        href = (raw_href[0] if isinstance(raw_href, list) else raw_href).strip()
        if not href or href.startswith("javascript:") or href.startswith("mailto:"):
            continue
        full_url = urljoin(base_url, href) if base_url else href
        text = a.get_text(strip=True)
        links.append({"text": text, "href": full_url})
    return links


def dom_to_markdown_summary(soup: BeautifulSoup) -> str:
    """Convert key semantic elements to clean markdown for LLM ingestion."""
    soup_copy = BeautifulSoup(str(soup), "html.parser")
    for tag in soup_copy(["script", "style", "noscript"]):
        tag.decompose()

    lines = []
    for tag in soup_copy.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = tag.get_text(strip=True)
        if not text:
            continue
        if tag.name == "h1":
            lines.append(f"# {text}")
        elif tag.name == "h2":
            lines.append(f"## {text}")
        elif tag.name == "h3":
            lines.append(f"### {text}")
        elif tag.name == "li":
            lines.append(f"- {text}")
        else:
            lines.append(text)
    return "\n\n".join(lines)
