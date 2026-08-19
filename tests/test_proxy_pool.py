import pytest

from foxcape.proxy_pool import ProxyConfig, ProxyPoolManager


def test_proxy_config_from_url_defaults() -> None:
    http = ProxyConfig.from_url("http://user:pass@example.com")
    socks = ProxyConfig.from_url("socks5://proxy.test")

    assert http.server == "http://example.com:8080"
    assert http.username == "user"
    assert http.password == "pass"
    assert socks.server == "socks5://proxy.test:1080"


def test_proxy_config_from_url_requires_hostname() -> None:
    with pytest.raises(ValueError, match="hostname"):
        ProxyConfig.from_url("http://")


def test_proxy_config_to_playwright_dict_omits_empty_credentials() -> None:
    assert ProxyConfig(server="http://example.com:8080").to_playwright_dict() == {"server": "http://example.com:8080"}


def test_proxy_pool_random_and_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    pool = ProxyPoolManager()
    assert pool.get_proxy() is None

    first = ProxyConfig(server="http://one:8080")
    second = ProxyConfig(server="http://two:8080")
    pool.add_proxy(first)
    pool.add_proxy(second)
    monkeypatch.setattr("foxcape.proxy_pool.random.choice", lambda items: items[-1])

    assert pool.get_proxy(strategy="random") == second
    assert pool.get_proxy(session_id="session") == second
    monkeypatch.setattr("foxcape.proxy_pool.random.choice", lambda items: items[0])
    assert pool.get_proxy(session_id="session") == second
