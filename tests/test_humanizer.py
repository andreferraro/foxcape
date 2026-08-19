"""WindMouse humanizer trajectory helpers."""

from foxcape.humanizer import generate_windmouse_path


def test_generate_windmouse_path_has_points_and_delays() -> None:
    path = generate_windmouse_path(0.0, 0.0, 200.0, 150.0)
    assert len(path) > 0
    for _x, _y, delay in path:
        assert delay >= 0


def test_generate_windmouse_path_endpoint_near_target() -> None:
    dest_x, dest_y = 120.0, 80.0
    path = generate_windmouse_path(10.0, 10.0, dest_x, dest_y)
    last_x, last_y, _ = path[-1]
    assert last_x == dest_x
    assert last_y == dest_y


def test_generate_windmouse_path_zero_distance() -> None:
    path = generate_windmouse_path(50.0, 50.0, 50.0, 50.0)
    assert len(path) == 1
    assert path[0][0] == 50.0
    assert path[0][1] == 50.0
