"""Smoke and contract tests aligned with specs/001-initial-release/spec.md."""

from pathlib import Path
from unittest.mock import patch

import foxcape


def test_smoke_import_all_public_symbols() -> None:
    """SC-003 / FR-002: every __all__ export is importable."""
    for name in foxcape.__all__:
        obj = getattr(foxcape, name)
        assert obj is not None


def test_smoke_import_does_not_touch_camoufox() -> None:
    """FR: importing package must never launch browser."""
    with patch("camoufox.sync_api.Camoufox") as mock_sync:
        with patch("camoufox.async_api.AsyncCamoufox") as mock_async:
            import importlib

            import foxcape as fc

            importlib.reload(fc)
            mock_sync.assert_not_called()
            mock_async.assert_not_called()


def test_contract_foxcape_config_has_documented_defaults() -> None:
    """FR-005: FoxcapeConfig fields have documented defaults."""
    cfg = foxcape.FoxcapeConfig()
    assert cfg.wait_until == "domcontentloaded"
    assert cfg.default_timeout_ms == 30000
    assert cfg.human_delay_range == (0.5, 2.0)
    assert cfg.parser_engine == "lxml"


def test_contract_result_helpers_do_not_require_browser() -> None:
    """FR-006: parsing helpers work offline on raw HTML."""
    html = """
    <html><head><title>Contract</title></head>
    <body><h1>H</h1><p>Body</p><a href="/x">Link</a></body></html>
    """
    result = foxcape.FoxcapeResult.from_html(html, url="https://site.example/page")
    assert result.get_clean_text()
    assert result.to_markdown()
    assert result.extract_links()
    assert result.select_one("h1") is not None


def test_contract_exceptions_hierarchy() -> None:
    """FR-009: minimal exception surface."""
    assert issubclass(foxcape.BrowserStartupError, foxcape.FoxcapeError)


def test_contract_proxy_pool_sticky_and_round_robin() -> None:
    """FR-007: pool supports round-robin and sticky sessions."""
    pool = foxcape.ProxyPoolManager()
    pool.add_proxy(foxcape.ProxyConfig(server="http://a:1"))
    pool.add_proxy(foxcape.ProxyConfig(server="http://b:2"))
    rr1 = pool.get_proxy(strategy="round_robin")
    rr2 = pool.get_proxy(strategy="round_robin")
    assert rr1 is not None
    assert rr2 is not None
    assert rr1.server != rr2.server
    sticky = pool.get_proxy(session_id="sess")
    assert sticky == pool.get_proxy(session_id="sess")


def test_contract_profile_to_config_sets_persistence(tmp_path: Path) -> None:
    """FR-008: profile converts to FoxcapeConfig with user_data_dir."""
    profile = foxcape.ProfileManager.get_or_create("_contract_profile", profiles_dir=tmp_path)
    cfg = profile.to_foxcape_config()
    assert cfg.user_data_dir == profile.profile_dir
    assert cfg.persistent_context is True
