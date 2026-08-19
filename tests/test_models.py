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
