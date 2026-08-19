"""FoxcapeConfig defaults."""

from foxcape import FoxcapeConfig


def test_config_defaults() -> None:
    cfg = FoxcapeConfig()
    assert cfg.headless is False
    assert cfg.humanize is True
    assert cfg.simulate_mouse is True
    assert cfg.canvas_noise is True
    assert cfg.audio_noise is True
    assert cfg.hardware_spoofing is True
    assert cfg.solve_turnstile is True
    assert cfg.use_markov_cadence is True
    assert cfg.geoip is True
    assert cfg.wait_until == "domcontentloaded"
    assert cfg.default_timeout_ms == 30000
    assert cfg.parser_engine == "lxml"
