"""Parser utilities: soup building, clean text, links, markdown."""

from unittest.mock import patch

from bs4 import BeautifulSoup

from foxcape.parsers import (
    build_soup,
    dom_to_markdown_summary,
    extract_clean_text,
    extract_links_from_soup,
)


def test_build_soup_uses_lxml_by_default(sample_html: str) -> None:
    soup = build_soup(sample_html)
    assert soup.find("title").get_text(strip=True) == "Test Page"


def test_build_soup_falls_back_to_html_parser_on_invalid_engine(sample_html: str) -> None:
    with patch(
        "foxcape.parsers.BeautifulSoup", side_effect=[Exception("boom"), BeautifulSoup(sample_html, "html.parser")]
    ):
        soup = build_soup(sample_html, parser_engine="broken-engine")
    assert soup.find("title") is not None


def test_extract_clean_text_strips_scripts_and_boilerplate() -> None:
    html = """
    <html><body>
    <header>Nav</header>
    <main><p>Visible<script>alert(1)</script></p></main>
    <footer>Footer</footer>
    <style>.x{}</style>
    </body></html>
    """
    text = extract_clean_text(build_soup(html))
    assert "Visible" in text
    assert "alert" not in text
    assert "Nav" not in text
    assert "Footer" not in text


def test_extract_clean_text_collapses_excessive_newlines() -> None:
    html = "<html><body><p>Line1</p><p></p><p></p><p>Line2</p></body></html>"
    text = extract_clean_text(build_soup(html))
    assert "\n\n\n" not in text


def test_extract_links_skips_javascript_and_mailto() -> None:
    html = """
    <html><body>
    <a href="javascript:void(0)">JS</a>
    <a href="mailto:a@b.com">Mail</a>
    <a href="/valid">Valid</a>
    </body></html>
    """
    links = extract_links_from_soup(build_soup(html), base_url="https://example.com")
    assert len(links) == 1
    assert links[0]["href"] == "https://example.com/valid"
    assert links[0]["text"] == "Valid"


def test_extract_links_handles_href_as_list() -> None:
    html = '<html><body><a href="/docs">Docs</a></body></html>'
    soup = build_soup(html)
    anchor = soup.find("a")
    anchor["href"] = ["/docs"]
    links = extract_links_from_soup(soup, base_url="https://example.com")
    assert links[0]["href"] == "https://example.com/docs"


def test_dom_to_markdown_summary_heading_levels() -> None:
    html = """
    <html><body>
    <h1>Title</h1>
    <h2>Section</h2>
    <h3>Sub</h3>
    <p>Body text</p>
    <ul><li>Item A</li><li>Item B</li></ul>
    </body></html>
    """
    md = dom_to_markdown_summary(build_soup(html))
    assert "# Title" in md
    assert "## Section" in md
    assert "### Sub" in md
    assert "Body text" in md
    assert "- Item A" in md


def test_dom_to_markdown_summary_skips_empty_tags() -> None:
    html = "<html><body><h1></h1><p>   </p><p>Content</p></body></html>"
    md = dom_to_markdown_summary(build_soup(html))
    assert "Content" in md
    assert md.count("#") == 0


def test_extract_links_empty_href_skipped() -> None:
    html = '<html><body><a href="">Empty</a><a>NoHref</a></body></html>'
    links = extract_links_from_soup(build_soup(html))
    assert links == []
