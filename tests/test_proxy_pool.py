"""ProxyConfig parsing and ProxyPoolManager selection strategies."""

from unittest.mock import patch

import pytest

from foxcape import ProxyConfig, ProxyPoolManager


def test_proxy_config_from_url_http_with_credentials() -> None:
    cfg = ProxyConfig.from_url("http://user:secret@proxy.example:3128")
    assert cfg.server == "http://proxy.example:3128"
    assert cfg.username == "user"
    assert cfg.password == "secret"
    assert cfg.protocol == "http"


def test_proxy_config_from_url_socks5_default_port() -> None:
    cfg = ProxyConfig.from_url("socks5://socks.example")
    assert cfg.server == "socks5://socks.example:1080"
    assert cfg.protocol == "socks5"


def test_proxy_config_from_url_defaults() -> None:
    http = ProxyConfig.from_url("http://user:pass@example.com")
    socks = ProxyConfig.from_url("socks5://proxy.test")
    assert http.server == "http://example.com:8080"
    assert http.username == "user"
    assert http.password == "pass"
    assert socks.server == "socks5://proxy.test:1080"


def test_proxy_config_to_playwright_dict_omits_empty_credentials() -> None:
    cfg = ProxyConfig(server="http://proxy:8080")
    assert cfg.to_playwright_dict() == {"server": "http://proxy:8080"}


def test_proxy_config_to_playwright_dict_includes_credentials() -> None:
    cfg = ProxyConfig(server="http://proxy:8080", username="u", password="p")
    d = cfg.to_playwright_dict()
    assert d["username"] == "u"
    assert d["password"] == "p"


def test_pool_init_from_url_strings() -> None:
    pool = ProxyPoolManager(["http://a:8080", "http://b:8080"])
    assert len(pool._proxies) == 2


def test_proxy_pool_empty_returns_none() -> None:
    pool = ProxyPoolManager()
    assert pool.get_proxy() is None


def test_pool_random_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    pool = ProxyPoolManager()
    pool.add_proxy(ProxyConfig(server="http://a:8080"))
    second = ProxyConfig(server="http://b:8080")
    pool.add_proxy(second)
    monkeypatch.setattr("foxcape.proxy_pool.rng.choice", lambda items: items[-1])
    assert pool.get_proxy(strategy="random") == second
    assert pool.get_proxy(session_id="session") == second


def test_pool_sticky_session_assigns_and_reuses() -> None:
    pool = ProxyPoolManager()
    pool.add_proxy(ProxyConfig(server="http://a:8080"))
    pool.add_proxy(ProxyConfig(server="http://b:8080"))
    with patch("foxcape.proxy_pool.rng.choice", return_value=pool._proxies[0]):
        first = pool.get_proxy(session_id="user-42")
    second = pool.get_proxy(session_id="user-42")
    assert first is second
    assert first.server == "http://a:8080"


def test_pool_round_robin_cycles() -> None:
    pool = ProxyPoolManager()
    pool.add_proxy(ProxyConfig(server="http://a:8080"))
    pool.add_proxy(ProxyConfig(server="http://b:8080"))
    servers = [pool.get_proxy(strategy="round_robin").server for _ in range(4)]
    assert servers == ["http://a:8080", "http://b:8080", "http://a:8080", "http://b:8080"]
