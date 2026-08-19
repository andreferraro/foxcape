"""MarkovCadence behavioral timing and state machine."""

from unittest.mock import patch

from bs4 import BeautifulSoup

from foxcape.cadence import MarkovCadence


def test_calculate_reading_dwell_time_respects_bounds_from_html() -> None:
    short_html = "<html><body><p>Hi</p></body></html>"
    dwell = MarkovCadence.calculate_reading_dwell_time(short_html, min_seconds=1.0, max_seconds=3.0)
    assert 1.0 <= dwell <= 3.0


def test_calculate_reading_dwell_time_from_soup_word_count() -> None:
    words = " ".join(["word"] * 500)
    soup = BeautifulSoup(f"<html><body><p>{words}</p></body></html>", "html.parser")
    dwell = MarkovCadence.calculate_reading_dwell_time(soup, min_seconds=0.5, max_seconds=4.5)
    assert 0.5 <= dwell <= 4.5


def test_calculate_reading_dwell_time_long_text_hits_max() -> None:
    huge = "x" * 100_000
    dwell = MarkovCadence.calculate_reading_dwell_time(huge, min_seconds=0.8, max_seconds=2.0)
    assert dwell <= 2.0


def test_generate_behavioral_sequence_starts_at_scan_header() -> None:
    with patch("foxcape.cadence.rng.uniform", side_effect=[0.5, 1.0, 0.3, 0.4]):
        with patch("foxcape.cadence.rng.choices", side_effect=[["READ_CONTENT"], ["DONE"]]):
            sequence = MarkovCadence.generate_behavioral_sequence(max_steps=3)
    assert sequence[0][0] == "SCAN_HEADER"
    assert all(duration > 0 for _, duration in sequence)


def test_generate_behavioral_sequence_can_reach_done() -> None:
    with patch("foxcape.cadence.rng.uniform", return_value=0.3):
        with patch("foxcape.cadence.rng.choices", return_value=["DONE"]):
            sequence = MarkovCadence.generate_behavioral_sequence(max_steps=5)
    states = [state for state, _ in sequence]
    assert "DONE" not in states or len(sequence) <= 5
