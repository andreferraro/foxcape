import json
import logging
import time
from datetime import datetime
from pathlib import Path

from . import rng
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

    def _default_metadata(self) -> dict:
        now = datetime.now().isoformat()
        return {
            "name": self.name,
            "created_at": now,
            "last_used_at": now,
            "visited_urls_count": 0,
            "warmup_completed": False,
            "warmup_category": None,
            "visited_domains": [],
        }

    def _load_metadata(self) -> dict:
        default_meta = self._default_metadata()
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    merged = {**default_meta, **loaded}
                    merged["name"] = self.name
                    if not isinstance(merged.get("visited_domains"), list):
                        merged["visited_domains"] = []
                    return merged
            except Exception:
                pass

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

    def _warmup_config(self, headless: bool) -> FoxcapeConfig:
        return self.to_foxcape_config(
            FoxcapeConfig(
                headless=headless,
                humanize=True,
                simulate_mouse=True,
                use_markov_cadence=True,
                canvas_noise=True,
                audio_noise=True,
            )
        )

    def _record_warmup_visit(self, url: str) -> None:
        self.metadata["visited_urls_count"] = self.metadata.get("visited_urls_count", 0) + 1
        domain = url.split("/")[2] if "//" in url else url
        if domain not in self.metadata["visited_domains"]:
            self.metadata["visited_domains"].append(domain)

    def _warmup_single_url(self, scraper: Foxcape, url: str, step: int, total: int, verbose: bool) -> None:
        if verbose:
            print(f"[*] [Warmup {step}/{total}] Visiting {url} and generating telemetry...", flush=True)
        t0 = time.time()
        result = scraper.get(
            url,
            wait_until="domcontentloaded",
            human_delay=True,
            simulate_mouse=True,
        )
        elapsed = time.time() - t0
        self._record_warmup_visit(url)
        if verbose:
            print(
                f"[+] [Warmup {step}/{total}] OK ({elapsed:.1f}s) - Title: {result.title[:45]}",
                flush=True,
            )

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
        selected_urls = rng.sample(seed_urls, min(steps, len(seed_urls)))

        if verbose:
            print(
                f"[*] [Warmup] Starting warmup for profile '{self.name}' ({len(selected_urls)} steps in category '{category}')...",
                flush=True,
            )

        config = self._warmup_config(headless=headless)
        successes = 0

        with Foxcape(config) as scraper:
            for i, url in enumerate(selected_urls, 1):
                try:
                    self._warmup_single_url(scraper, url, i, len(selected_urls), verbose)
                    successes += 1
                except Exception as e:
                    if verbose:
                        print(f"[!] [Warmup {i}/{len(selected_urls)}] Warning: failed to visit {url}: {e}", flush=True)

        warmed = successes > 0
        self.metadata["warmup_completed"] = warmed or self.is_warm
        self.metadata["warmup_category"] = category
        self.metadata["last_used_at"] = datetime.now().isoformat()
        self._save_metadata()

        if verbose and warmed:
            print(f"[+] [Warmup] Completed successfully! Profile '{self.name}' is ready for production.\n", flush=True)
        elif verbose:
            print(f"[!] [Warmup] No steps completed for profile '{self.name}'.\n", flush=True)
        return warmed


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
