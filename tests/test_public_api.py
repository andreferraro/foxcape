"""Public API surface and import hygiene."""

import importlib
from pathlib import Path
from unittest.mock import patch

import foxcape
from foxcape import (
    AsyncFoxcape,
    BrowserStartupError,
    Foxcape,
    FoxcapeConfig,
    FoxcapeError,
    FoxcapeResult,
    ProfileManager,
    ProxyConfig,
    ProxyPoolManager,
)


def test_version() -> None:
    assert foxcape.__version__ == "0.1.1"


def test_all_exports_importable() -> None:
    for name in foxcape.__all__:
        assert hasattr(foxcape, name), f"missing export: {name}"


def test_core_types() -> None:
    assert Foxcape is not None
    assert AsyncFoxcape is not None
    assert issubclass(BrowserStartupError, FoxcapeError)
    assert FoxcapeConfig() is not None
    assert FoxcapeResult.from_html("<html></html>") is not None


def test_proxy_pool_strategies() -> None:
    pool = ProxyPoolManager()
    pool.add_proxy(ProxyConfig(server="http://proxy1:8080"))
    pool.add_proxy(ProxyConfig(server="http://proxy2:8080"))
    first = pool.get_proxy(strategy="round_robin")
    second = pool.get_proxy(strategy="round_robin")
    assert first is not None
    assert second is not None
    assert first.server != second.server
    sticky = pool.get_proxy(session_id="sess-1")
    assert sticky == pool.get_proxy(session_id="sess-1")


def test_profile_manager(tmp_path: Path) -> None:
    assert ProfileManager.get_or_create("_test_profile_unit", profiles_dir=tmp_path)


@patch("camoufox.async_api.AsyncCamoufox")
@patch("camoufox.sync_api.Camoufox")
def test_import_does_not_start_browser(mock_sync_camoufox, mock_async_camoufox) -> None:
    """Importing foxcape must not launch Camoufox."""
    importlib.reload(foxcape)
    mock_sync_camoufox.assert_not_called()
    mock_async_camoufox.assert_not_called()


def test_empty_proxy_pool_returns_none() -> None:
    pool = ProxyPoolManager()
    assert pool.get_proxy() is None
    assert pool.get_proxy(strategy="round_robin") is None
    assert pool.get_proxy(session_id="sess-empty") is None
