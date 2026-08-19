import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path

from .config import FoxcapeConfig
from .scraper import Foxcape

logger = logging.getLogger("foxcape.profiles")

WARMUP_SEEDS: dict[str, list[str]] = {
    "general": [
        "https://www.wikipedia.org",
        "https://duckduckgo.com",
        "https://news.ycombinator.com",
        "https://www.bbc.com",
        "https://github.com",
    ],
    "sports": [
        "https://www.espn.com",
        "https://www.wikipedia.org/wiki/Futebol",
        "https://globoesporte.globo.com",
        "https://www.flashscore.com",
    ],
    "ecommerce": [
        "https://www.mercadolivre.com.br",
        "https://www.amazon.com",
        "https://www.wikipedia.org/wiki/E-commerce",
    ],
}


class BrowserProfile:
    """Represents a persistent browser profile with disk storage, cookies, and trust metadata."""

    def __init__(self, profile_name: str, profiles_dir: Path):
        self.name = profile_name
        self.profile_dir = profiles_dir / profile_name
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.profile_dir / "profile_metadata.json"
        self.metadata = self._load_metadata()

    def clean_lock(self):
        """Cleans stale parent.lock file if left by previous unclean termination."""
        lock_file = self.profile_dir / "parent.lock"
        if lock_file.exists():
            try:
                lock_file.unlink()
            except Exception:
                pass

    def _load_metadata(self) -> dict:
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        default_meta = {
            "name": self.name,
            "created_at": datetime.now().isoformat(),
            "last_used_at": datetime.now().isoformat(),
            "visited_urls_count": 0,
            "warmup_completed": False,
            "warmup_category": None,
            "visited_domains": [],
        }
        self._save_metadata(default_meta)
        return default_meta

    def _save_metadata(self, data: dict | None = None):
        if data is not None:
            self.metadata = data
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

    @property
    def is_warm(self) -> bool:
        """Returns True if this profile has undergone organic warmup."""
        return bool(self.metadata.get("warmup_completed", False))

    @property
    def age_days(self) -> float:
        """Returns the age of this profile in days."""
        created_str = self.metadata.get("created_at")
        if not created_str:
            return 0.0
        created = datetime.fromisoformat(created_str)
        return (datetime.now() - created).total_seconds() / 86400.0

    def to_foxcape_config(self, base_config: FoxcapeConfig | None = None) -> FoxcapeConfig:
        """Converts profile into a persistent FoxcapeConfig instance with stale lock cleanup."""
        self.clean_lock()
        cfg = base_config or FoxcapeConfig()
        cfg.user_data_dir = self.profile_dir
        cfg.persistent_context = True
        return cfg

    def warmup(
        self,
        category: str = "general",
        steps: int = 2,
        headless: bool = True,
        verbose: bool = True,
    ) -> bool:
        """
        Executes an organic warmup sequence by browsing trusted domains,
        moving the mouse realistically (WindMouse), and acquiring trust cookies and cache.
        """
        self.clean_lock()
        seed_urls = WARMUP_SEEDS.get(category, WARMUP_SEEDS["general"])
        selected_urls = random.sample(seed_urls, min(steps, len(seed_urls)))

        if verbose:
            print(
                f"[*] [Warmup] Iniciando aquecimento do perfil '{self.name}' ({len(selected_urls)} etapas na categoria '{category}')...",
                flush=True,
            )

        config = self.to_foxcape_config(
            FoxcapeConfig(
                headless=headless,
                humanize=True,
                simulate_mouse=True,
                use_markov_cadence=True,
                canvas_noise=True,
                audio_noise=True,
            )
        )

        with Foxcape(config) as scraper:
            for i, url in enumerate(selected_urls, 1):
                try:
                    if verbose:
                        print(
                            f"[*] [Warmup {i}/{len(selected_urls)}] Acessando {url} e gerando telemetria...", flush=True
                        )

                    t0 = time.time()
                    result = scraper.get(
                        url,
                        wait_until="domcontentloaded",
                        human_delay=True,
                        simulate_mouse=True,
                    )
                    elapsed = time.time() - t0

                    self.metadata["visited_urls_count"] = self.metadata.get("visited_urls_count", 0) + 1
                    domain = url.split("/")[2] if "//" in url else url
                    if domain not in self.metadata["visited_domains"]:
                        self.metadata["visited_domains"].append(domain)

                    if verbose:
                        print(
                            f"[+] [Warmup {i}/{len(selected_urls)}] OK ({elapsed:.1f}s) - Titulo: {result.title[:45]}",
                            flush=True,
                        )
                except Exception as e:
                    if verbose:
                        print(f"[!] [Warmup {i}/{len(selected_urls)}] Aviso: falha ao acessar {url}: {e}", flush=True)

        self.metadata["warmup_completed"] = True
        self.metadata["warmup_category"] = category
        self.metadata["last_used_at"] = datetime.now().isoformat()
        self._save_metadata()

        if verbose:
            print(f"[+] [Warmup] Concluido com sucesso! Perfil '{self.name}' pronto para producao.\n", flush=True)
        return True


class ProfileManager:
    """Manages creation, retrieval, and warmup lifecycle of persistent browser profiles."""

    DEFAULT_PROFILES_DIR = Path(".profiles")

    @classmethod
    def get_or_create(
        cls,
        name: str = "default_stealth_profile",
        profiles_dir: Path | None = None,
    ) -> BrowserProfile:
        base_dir = profiles_dir or cls.DEFAULT_PROFILES_DIR
        return BrowserProfile(profile_name=name, profiles_dir=base_dir)

    @classmethod
    def list_profiles(cls, profiles_dir: Path | None = None) -> list[BrowserProfile]:
        base_dir = profiles_dir or cls.DEFAULT_PROFILES_DIR
        if not base_dir.exists():
            return []
        profiles = []
        for p in base_dir.iterdir():
            if p.is_dir() and (p / "profile_metadata.json").exists():
                profiles.append(BrowserProfile(profile_name=p.name, profiles_dir=base_dir))
        return profiles
