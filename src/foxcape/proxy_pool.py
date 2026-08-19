import random
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ProxyConfig:
    """Represents proxy credentials and endpoint information."""

    server: str
    username: str | None = None
    password: str | None = None
    protocol: str = "http"

    @classmethod
    def from_url(cls, proxy_url: str) -> "ProxyConfig":
        """
        Parses standard proxy URL format:
        http://user:pass@host:port or socks5://host:port
        """
        parsed = urlparse(proxy_url)
        scheme = parsed.scheme or "http"

        username = parsed.username
        password = parsed.password
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Proxy URL must include a hostname.")
        port = parsed.port or (8080 if scheme.startswith("http") else 1080)

        server = f"{scheme}://{hostname}:{port}"
        return cls(server=server, username=username, password=password, protocol=scheme)

    def to_playwright_dict(self) -> dict[str, str]:
        """Converts to Playwright/Camoufox proxy dictionary format."""
        d = {"server": self.server}
        if self.username:
            d["username"] = self.username
        if self.password:
            d["password"] = self.password
        return d


class ProxyPoolManager:
    """Manages rotating proxy pools with sticky session support and health tracking."""

    def __init__(self, proxies: list[str | ProxyConfig] | None = None):
        self._proxies: list[ProxyConfig] = []
        self._sticky_sessions: dict[str, ProxyConfig] = {}
        self._index = 0

        if proxies:
            for p in proxies:
                self.add_proxy(p)

    def add_proxy(self, proxy: str | ProxyConfig):
        if isinstance(proxy, str):
            self._proxies.append(ProxyConfig.from_url(proxy))
        else:
            self._proxies.append(proxy)

    def get_proxy(
        self,
        strategy: str = "round_robin",
        session_id: str | None = None,
    ) -> ProxyConfig | None:
        """
        Retrieves a proxy based on selected strategy ('round_robin', 'random', 'sticky').
        """
        if not self._proxies:
            return None

        if session_id:
            if session_id not in self._sticky_sessions:
                self._sticky_sessions[session_id] = random.choice(self._proxies)
            return self._sticky_sessions[session_id]

        if strategy == "random":
            return random.choice(self._proxies)

        # Round robin
        proxy = self._proxies[self._index % len(self._proxies)]
        self._index += 1
        return proxy
