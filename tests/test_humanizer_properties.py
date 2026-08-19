"""Property-based tests for WindMouse trajectory generation."""

from __future__ import annotations

import math

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from foxcape.humanizer import generate_windmouse_path

MIN_TRAVEL = 10.0  # px — WindMouse loop runs while dist > 1.0


def _distance_to(x: float, y: float, dest_x: float, dest_y: float) -> float:
    return math.hypot(dest_x - x, dest_y - y)


def _distances_to_target(
    path: list[tuple[float, float, float]],
    dest_x: float,
    dest_y: float,
) -> list[float]:
    return [_distance_to(x, y, dest_x, dest_y) for x, y, _ in path]


@st.composite
def mouse_travel(draw: st.DrawFn, *, min_travel: float = MIN_TRAVEL) -> tuple[float, float, float, float]:
    """Generate start/dest pairs with guaranteed meaningful travel distance."""
    start_x = draw(st.floats(min_value=0.0, max_value=1800.0, allow_nan=False, allow_infinity=False))
    start_y = draw(st.floats(min_value=0.0, max_value=900.0, allow_nan=False, allow_infinity=False))
    angle = draw(st.floats(min_value=0.0, max_value=2 * math.pi, allow_nan=False, allow_infinity=False))
    travel = draw(st.floats(min_value=min_travel, max_value=600.0, allow_nan=False, allow_infinity=False))
    dest_x = min(1920.0, max(0.0, start_x + math.cos(angle) * travel))
    dest_y = min(1080.0, max(0.0, start_y + math.sin(angle) * travel))
    assume(_distance_to(start_x, start_y, dest_x, dest_y) >= min_travel)
    return start_x, start_y, dest_x, dest_y


@st.composite
def zero_travel(draw: st.DrawFn) -> tuple[float, float, float, float]:
    x = draw(st.floats(min_value=0.0, max_value=1920.0, allow_nan=False, allow_infinity=False))
    y = draw(st.floats(min_value=0.0, max_value=1080.0, allow_nan=False, allow_infinity=False))
    return x, y, x, y


@given(mouse_travel())
@settings(max_examples=150, deadline=None)
def test_path_always_ends_exactly_at_destination(
    coords: tuple[float, float, float, float],
) -> None:
    start_x, start_y, dest_x, dest_y = coords
    path = generate_windmouse_path(start_x, start_y, dest_x, dest_y)
    last_x, last_y, _ = path[-1]
    assert last_x == dest_x
    assert last_y == dest_y


@given(mouse_travel())
@settings(max_examples=150, deadline=None)
def test_path_delays_are_non_negative(coords: tuple[float, float, float, float]) -> None:
    start_x, start_y, dest_x, dest_y = coords
    path = generate_windmouse_path(start_x, start_y, dest_x, dest_y)
    for _x, _y, delay in path:
        assert delay >= 0.0


@given(zero_travel())
@settings(max_examples=50, deadline=None)
def test_zero_distance_yields_single_point_at_origin(
    coords: tuple[float, float, float, float],
) -> None:
    start_x, start_y, dest_x, dest_y = coords
    path = generate_windmouse_path(start_x, start_y, dest_x, dest_y)
    assert len(path) == 1
    assert path[0][0] == start_x
    assert path[0][1] == start_y


@given(mouse_travel())
@settings(max_examples=150, deadline=None)
def test_non_zero_distance_produces_at_least_two_points(
    coords: tuple[float, float, float, float],
) -> None:
    start_x, start_y, dest_x, dest_y = coords
    path = generate_windmouse_path(start_x, start_y, dest_x, dest_y)
    assert len(path) >= 2


@given(mouse_travel())
@settings(max_examples=150, deadline=None)
def test_net_progress_reduces_distance_to_target(
    coords: tuple[float, float, float, float],
) -> None:
    start_x, start_y, dest_x, dest_y = coords
    initial = _distance_to(start_x, start_y, dest_x, dest_y)
    path = generate_windmouse_path(start_x, start_y, dest_x, dest_y)
    final = _distance_to(path[-1][0], path[-1][1], dest_x, dest_y)
    assert final == 0.0
    assert initial > final

    path_length = sum(
        math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1]) for i in range(len(path) - 1)
    )
    # WindMouse may overshoot; path should stay within a reasonable factor of the direct segment.
    assert path_length <= initial * 4.0 + 50.0


@given(mouse_travel())
@settings(max_examples=150, deadline=None)
def test_distance_to_target_is_monotone_in_running_minimum(
    coords: tuple[float, float, float, float],
) -> None:
    """Running minimum distance to destination converges to zero — the path always gets closer eventually."""
    start_x, start_y, dest_x, dest_y = coords
    initial = _distance_to(start_x, start_y, dest_x, dest_y)
    path = generate_windmouse_path(start_x, start_y, dest_x, dest_y)
    dists = _distances_to_target(path, dest_x, dest_y)

    running_min = dists[0]
    for dist in dists[1:]:
        running_min = min(running_min, dist)
        assert running_min <= initial + 1.0

    assert running_min <= 1.0
    assert dists[-1] == 0.0


@given(mouse_travel())
@settings(max_examples=150, deadline=None)
def test_majority_of_steps_reduce_distance_to_target(
    coords: tuple[float, float, float, float],
) -> None:
    """Most steps move closer to the destination (wind/jitter may cause occasional regressions)."""
    start_x, start_y, dest_x, dest_y = coords
    path = generate_windmouse_path(start_x, start_y, dest_x, dest_y)
    dists = _distances_to_target(path, dest_x, dest_y)

    improvements = sum(1 for i in range(len(dists) - 1) if dists[i + 1] < dists[i] - 1e-9)
    regressions = sum(1 for i in range(len(dists) - 1) if dists[i + 1] > dists[i] + 1e-9)
    assert improvements >= regressions


@given(
    start_x=st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
    start_y=st.floats(min_value=0, max_value=500, allow_nan=False, allow_infinity=False),
    delta_x=st.floats(min_value=80, max_value=800, allow_nan=False, allow_infinity=False),
    delta_y=st.floats(min_value=80, max_value=600, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=80, deadline=None)
def test_longer_distance_yields_more_steps_than_short_hop(
    start_x: float,
    start_y: float,
    delta_x: float,
    delta_y: float,
) -> None:
    """Step count scales with travel distance (same start, longer leg → more points)."""
    short_dest_x = start_x + delta_x * 0.25
    short_dest_y = start_y + delta_y * 0.25
    long_dest_x = start_x + delta_x
    long_dest_y = start_y + delta_y

    short_dist = _distance_to(start_x, start_y, short_dest_x, short_dest_y)
    long_dist = _distance_to(start_x, start_y, long_dest_x, long_dest_y)
    assume(short_dist >= MIN_TRAVEL and long_dist >= MIN_TRAVEL * 2)

    short_path = generate_windmouse_path(start_x, start_y, short_dest_x, short_dest_y)
    long_path = generate_windmouse_path(start_x, start_y, long_dest_x, long_dest_y)
    assert len(long_path) >= len(short_path)
