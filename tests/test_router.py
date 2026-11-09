import pytest

from core import router


def test_lux_to_millilux():
    assert router.lux_to_millilux(0.5) == pytest.approx(500)


@pytest.mark.parametrize("mlx, dark", [(0, True), (499, True), (500, False), (501, False)])
def test_dark_boundary(mlx, dark):
    assert router.is_dark(mlx) is dark


@pytest.mark.parametrize("water, temp, ice", [
    (1001, -1, True), (1000, -1, False), (1001, 0, False), (1000, 0, False), (5000, -20, True),
])
def test_black_ice_boundary(water, temp, ice):
    assert router.is_black_ice(water, temp) is ice


@pytest.mark.parametrize("mlx, water, temp, use_nn", [
    (500, 1000, -1, False),  # SpeedLimit10b table
    (500, 1001, 0, False),
    (500, 1001, -1, True),
    (499, 1000, -1, True),
    (499, 0, 20, True),
    (100000, 5000, -10, True),
    (100000, 5000, 5, False),
])
def test_route(mlx, water, temp, use_nn):
    assert router.route(mlx, water, temp).use_nn is use_nn


def test_route_reports_both_reasons():
    decision = router.route(100, 2000, -5)
    assert decision.dark and decision.black_ice
