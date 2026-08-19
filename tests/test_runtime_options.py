from foxcape import FoxcapeConfig
from foxcape.proxy_pool import ProxyConfig
from foxcape.runtime_options import build_camoufox_kwargs


def test_build_camoufox_kwargs_minimal() -> None:
    assert build_camoufox_kwargs(FoxcapeConfig()) == {
        "headless": False,
        "humanize": True,
        "geoip": True,
        "os": "windows",
    }


def test_build_camoufox_kwargs_with_all_optional_fields(tmp_path) -> None:
    cfg = FoxcapeConfig(
        headless=True,
        humanize=False,
        geoip=False,
        os=["windows"],
        fingerprint_preset={"screen": "desktop"},
        disable_coop=True,
        i_know_what_im_doing=True,
        geoip_db="geo.mmdb",
        block_images=True,
        block_webrtc=True,
        block_webgl=True,
        enable_cache=True,
        window=(1280, 720),
        locale=["en-US"],
        fonts=["Arial"],
        proxy=ProxyConfig(server="http://proxy:8080", username="user", password="pass"),
        user_data_dir=tmp_path,
        persistent_context=True,
    )

    kwargs = build_camoufox_kwargs(cfg)

    assert kwargs["fingerprint_preset"] == {"screen": "desktop"}
    assert kwargs["disable_coop"] is True
    assert kwargs["i_know_what_im_doing"] is True
    assert kwargs["enable_cache"] is True
    assert kwargs["proxy"] == {"server": "http://proxy:8080", "username": "user", "password": "pass"}
    assert kwargs["user_data_dir"] == str(tmp_path)
    assert kwargs["persistent_context"] is True
