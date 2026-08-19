import json
from datetime import datetime, timedelta
from types import SimpleNamespace

from foxcape import FoxcapeConfig
from foxcape.profiles import BrowserProfile, ProfileManager


def test_profile_metadata_lifecycle(tmp_path) -> None:
    profile = BrowserProfile("unit", tmp_path)

    assert profile.metadata["name"] == "unit"
    assert profile.is_warm is False
    assert profile.age_days >= 0

    profile.metadata["warmup_completed"] = True
    profile._save_metadata()

    loaded = BrowserProfile("unit", tmp_path)
    assert loaded.is_warm is True


def test_profile_handles_missing_and_existing_metadata(tmp_path) -> None:
    profile_dir = tmp_path / "broken"
    profile_dir.mkdir()
    (profile_dir / "profile_metadata.json").write_text("{", encoding="utf-8")

    profile = BrowserProfile("broken", tmp_path)
    assert profile.metadata["name"] == "broken"

    old = datetime.now() - timedelta(days=2)
    profile.metadata["created_at"] = old.isoformat()
    profile._save_metadata()
    assert BrowserProfile("broken", tmp_path).age_days >= 1.9


def test_profile_config_and_listing(tmp_path) -> None:
    profile = BrowserProfile("unit", tmp_path)
    lock_file = profile.profile_dir / "parent.lock"
    lock_file.write_text("stale", encoding="utf-8")

    cfg = profile.to_foxcape_config(FoxcapeConfig(headless=True))
    assert cfg.user_data_dir == profile.profile_dir
    assert cfg.persistent_context is True
    assert not lock_file.exists()

    assert [p.name for p in ProfileManager.list_profiles(tmp_path)] == ["unit"]
    assert ProfileManager.list_profiles(tmp_path / "missing") == []


def test_profile_manager_get_or_create(tmp_path) -> None:
    profile = ProfileManager.get_or_create("created", tmp_path)
    assert json.loads(profile.metadata_file.read_text(encoding="utf-8"))["name"] == "created"


def test_profile_warmup_success(monkeypatch, tmp_path) -> None:
    class FakeFoxcape:
        def __init__(self, config) -> None:
            self.config = config

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            return None

        def get(self, url, wait_until, human_delay, simulate_mouse):
            return SimpleNamespace(title=f"Title {url}")

    monkeypatch.setattr("foxcape.profiles.Foxcape", FakeFoxcape)
    monkeypatch.setattr("foxcape.profiles.random.sample", lambda urls, count: urls[:count])
    monkeypatch.setattr("foxcape.profiles.time.time", iter([1.0, 2.0, 3.0, 4.0]).__next__)

    profile = BrowserProfile("warm", tmp_path)
    assert profile.warmup(category="sports", steps=2, verbose=True) is True
    assert profile.metadata["warmup_completed"] is True
    assert profile.metadata["warmup_category"] == "sports"
    assert profile.metadata["visited_urls_count"] == 2


def test_profile_warmup_continues_after_fetch_error(monkeypatch, tmp_path) -> None:
    class FailingFoxcape:
        def __init__(self, config) -> None:
            self.config = config

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> None:
            return None

        def get(self, url, wait_until, human_delay, simulate_mouse):
            raise RuntimeError("network")

    monkeypatch.setattr("foxcape.profiles.Foxcape", FailingFoxcape)
    monkeypatch.setattr("foxcape.profiles.random.sample", lambda urls, count: urls[:count])

    profile = BrowserProfile("warm-failure", tmp_path)
    assert profile.warmup(category="missing", steps=1, verbose=True) is True
    assert profile.metadata["warmup_completed"] is True
    assert profile.metadata["visited_urls_count"] == 0
