"""Shared fixtures for Foxcape tests."""

import pytest

from foxcape import FoxcapeConfig

SAMPLE_HTML = """<!DOCTYPE html><html><head><title>Test Page</title></head>
<body><header><nav><a href="/home">Home</a></nav></header>
<main><h1>Main Heading</h1><p>Paragraph<script>console.log("x");</script></p></main>
</body></html>"""


@pytest.fixture
def default_config() -> FoxcapeConfig:
    return FoxcapeConfig(headless=True, humanize=False, simulate_mouse=False)


@pytest.fixture
def sample_html() -> str:
    return SAMPLE_HTML
