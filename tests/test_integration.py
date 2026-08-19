"""Live integration tests (require Camoufox browser + network)."""

import pytest

from foxcape import AsyncFoxcape, Foxcape, FoxcapeConfig

pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_live_async_example_com() -> None:
    config = FoxcapeConfig(headless=True, humanize=False, simulate_mouse=False, human_delay_range=None)
    result = await AsyncFoxcape.afetch("https://example.com", config=config, human_delay=False)
    assert result.status_code == 200
    assert "Example Domain" in (result.title or "")


def test_live_sync_example_com() -> None:
    config = FoxcapeConfig(headless=True, humanize=False, simulate_mouse=False, human_delay_range=None)
    result = Foxcape.fetch("https://example.com", config=config, human_delay=False)
    assert result.status_code == 200
    assert "Example Domain" in (result.title or "")
