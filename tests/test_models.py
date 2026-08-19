"""FoxcapeResult parsing helpers."""

from foxcape import FoxcapeResult


def test_from_html(sample_html: str) -> None:
    result = FoxcapeResult.from_html(sample_html, url="https://example.com/test")
    assert result.title == "Test Page"
    assert result.select_one("h1") is not None
    assert result.select_one("h1").get_text(strip=True) == "Main Heading"
    assert len(result.extract_links()) >= 1
    assert "console.log" not in result.get_clean_text()
    markdown = result.to_markdown()
    assert "Main Heading" in markdown or "#" in markdown


def test_from_html_empty() -> None:
    result = FoxcapeResult.from_html("", url="https://example.com")
    assert result.title == ""
    assert result.get_clean_text() == ""


def test_from_html_does_not_mutate_input_html() -> None:
    html = "<html><head><title>T</title></head><body><p>Hi</p></body></html>"
    original = html
    result = FoxcapeResult.from_html(html, url="https://example.com")
    assert result.html == original
    assert result.select("p")[0].get_text() == "Hi"


def test_select_returns_multiple_matches() -> None:
    html = "<html><body><p class='x'>A</p><p class='x'>B</p></body></html>"
    result = FoxcapeResult.from_html(html)
    assert len(result.select("p.x")) == 2


def test_extract_links_resolves_relative_urls() -> None:
    html = '<html><body><a href="/docs">Docs</a><a href="page.html">Page</a></body></html>'
    result = FoxcapeResult.from_html(html, url="https://example.com/app/")
    hrefs = {link["href"] for link in result.extract_links()}
    assert "https://example.com/docs" in hrefs
    assert "https://example.com/app/page.html" in hrefs
