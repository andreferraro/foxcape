"""Browser profile metadata and warmup (Foxcape mocked)."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from foxcape import FoxcapeConfig, FoxcapeResult, ProfileManager
from foxcape.profiles import BrowserProfile


def test_profile_metadata_lifecycle(tmp_path: Path) -> None:
    profile = BrowserProfile("unit", tmp_path)
    assert profile.metadata["name"] == "unit"
    assert profile.is_warm is False
    assert profile.age_days >= 0

    profile.metadata["warmup_completed"] = True
    profile._save_metadata()
    assert BrowserProfile("unit", tmp_path).is_warm is True


def test_profile_handles_missing_and_existing_metadata(tmp_path: Path) -> None:
    profile_dir = tmp_path / "broken"
    profile_dir.mkdir()
    (profile_dir / "profile_metadata.json").write_text("{", encoding="utf-8")

    profile = BrowserProfile("broken", tmp_path)
    assert profile.metadata["name"] == "broken"

    old = datetime.now() - timedelta(days=2)
    profile.metadata["created_at"] = old.isoformat()
    profile._save_metadata()
    assert BrowserProfile("broken", tmp_path).age_days >= 1.9


def test_profile_metadata_and_to_foxcape_config(tmp_path: Path) -> None:
    profile = ProfileManager.get_or_create("unit_profile", profiles_dir=tmp_path)
    assert profile.metadata_file.exists()
    assert profile.name == "unit_profile"
    assert profile.is_warm is False

    lock_file = profile.profile_dir / "parent.lock"
    lock_file.write_text("stale", encoding="utf-8")
    cfg = profile.to_foxcape_config(FoxcapeConfig(headless=True))
    assert cfg.user_data_dir == profile.profile_dir
    assert cfg.persistent_context is True
    assert not lock_file.exists()


def test_profile_config_and_listing(tmp_path: Path) -> None:
    ProfileManager.get_or_create("unit", profiles_dir=tmp_path)
    assert [p.name for p in ProfileManager.list_profiles(tmp_path)] == ["unit"]
    assert ProfileManager.list_profiles(tmp_path / "missing") == []


def test_profile_manager_get_or_create(tmp_path: Path) -> None:
    profile = ProfileManager.get_or_create("created", profiles_dir=tmp_path)
    assert json.loads(profile.metadata_file.read_text(encoding="utf-8"))["name"] == "created"


def test_profile_warmup_success(monkeypatch, tmp_path: Path) -> None:
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
    monkeypatch.setattr("foxcape.profiles.rng.sample", lambda urls, count: urls[:count])
    monkeypatch.setattr("foxcape.profiles.time.time", iter([1.0, 2.0, 3.0, 4.0]).__next__)

    profile = BrowserProfile("warm", tmp_path)
    assert profile.warmup(category="sports", steps=2, verbose=True) is True
    assert profile.metadata["warmup_completed"] is True
    assert profile.metadata["warmup_category"] == "sports"
    assert profile.metadata["visited_urls_count"] == 2


def test_profile_warmup_all_failures_returns_false(monkeypatch, tmp_path: Path) -> None:
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
    monkeypatch.setattr("foxcape.profiles.rng.sample", lambda urls, count: urls[:count])

    profile = BrowserProfile("warm-failure", tmp_path)
    assert profile.warmup(category="missing", steps=1, verbose=True) is False
    assert profile.metadata["warmup_completed"] is False
    assert profile.metadata["visited_urls_count"] == 0


def test_clean_lock_removes_stale_lock(tmp_path: Path) -> None:
    profile = ProfileManager.get_or_create("lock_test", profiles_dir=tmp_path)
    lock_file = profile.profile_dir / "parent.lock"
    lock_file.write_text("stale", encoding="utf-8")
    profile.clean_lock()
    assert not lock_file.exists()


@patch("foxcape.profiles.Foxcape")
def test_warmup_updates_metadata(mock_foxcape_cls: MagicMock, tmp_path: Path) -> None:
    mock_instance = MagicMock()
    mock_instance.__enter__ = MagicMock(return_value=mock_instance)
    mock_instance.__exit__ = MagicMock(return_value=False)
    mock_instance.get.return_value = FoxcapeResult.from_html(
        "<html><head><title>Warm</title></head><body></body></html>"
    )
    mock_foxcape_cls.return_value = mock_instance

    profile = ProfileManager.get_or_create("warm_profile", profiles_dir=tmp_path)
    assert profile.warmup(category="general", steps=1, verbose=False) is True
    assert profile.is_warm is True
    assert profile.metadata.get("warmup_category") == "general"
    mock_instance.get.assert_called()


def test_list_profiles(tmp_path: Path) -> None:
    ProfileManager.get_or_create("alpha", profiles_dir=tmp_path)
    ProfileManager.get_or_create("beta", profiles_dir=tmp_path)
    names = {p.name for p in ProfileManager.list_profiles(profiles_dir=tmp_path)}
    assert names == {"alpha", "beta"}


def test_list_profiles_empty_when_dir_missing(tmp_path: Path) -> None:
    assert ProfileManager.list_profiles(profiles_dir=tmp_path / "missing") == []


def test_profile_age_days_from_metadata(tmp_path: Path) -> None:
    profile = ProfileManager.get_or_create("aged", profiles_dir=tmp_path)
    profile.metadata["created_at"] = (datetime.now() - timedelta(days=3)).isoformat()
    profile._save_metadata()
    reloaded = ProfileManager.get_or_create("aged", profiles_dir=tmp_path)
    assert reloaded.age_days >= 2.9


def test_profile_loads_default_metadata_on_corrupt_json(tmp_path: Path) -> None:
    profile = ProfileManager.get_or_create("corrupt", profiles_dir=tmp_path)
    profile.metadata_file.write_text("{not json", encoding="utf-8")
    reloaded = ProfileManager.get_or_create("corrupt", profiles_dir=tmp_path)
    assert reloaded.metadata["name"] == "corrupt"
    assert reloaded.metadata_file.exists()


@patch("foxcape.profiles.Foxcape")
def test_warmup_partial_failure_still_usable(mock_foxcape_cls: MagicMock, tmp_path: Path) -> None:
    mock_instance = MagicMock()
    mock_instance.__enter__ = MagicMock(return_value=mock_instance)
    mock_instance.__exit__ = MagicMock(return_value=False)
    mock_instance.get.side_effect = [
        FoxcapeResult.from_html("<html><head><title>OK</title></head></html>"),
        RuntimeError("blocked"),
    ]
    mock_foxcape_cls.return_value = mock_instance

    profile = ProfileManager.get_or_create("partial_warm", profiles_dir=tmp_path)
    assert profile.warmup(category="general", steps=2, verbose=False) is True
    assert profile.is_warm is True
    assert profile.metadata["visited_urls_count"] >= 1


@patch("foxcape.profiles.Foxcape")
def test_warmup_all_failures_via_manager(mock_foxcape_cls: MagicMock, tmp_path: Path) -> None:
    mock_instance = MagicMock()
    mock_instance.__enter__ = MagicMock(return_value=mock_instance)
    mock_instance.__exit__ = MagicMock(return_value=False)
    mock_instance.get.side_effect = RuntimeError("network down")
    mock_foxcape_cls.return_value = mock_instance

    profile = ProfileManager.get_or_create("cold", profiles_dir=tmp_path)
    assert profile.warmup(category="sports", steps=1, verbose=False) is False
    assert profile.is_warm is False
