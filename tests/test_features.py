import math

import pytest

from core import features
from tests.helpers import NIGHT_READINGS, hourly_table


def test_column_order_is_fixed():
    assert list(features.FEATURES) == [
        "speed_limit", "log_lux", "water_um", "temperature_c", "wind_strength",
        "humidity_pct", "traffic_cars_s", "is_dark", "is_black_ice",
    ]
    assert list(features.training_matrix(hourly_table(1)).columns) == list(features.FEATURES)


def test_log_lux():
    table = hourly_table(1, lux=99.0)
    assert features.training_matrix(table)["log_lux"].iloc[0] == pytest.approx(math.log(100))


def test_live_matrix_has_one_row_per_candidate():
    matrix = features.live_matrix(NIGHT_READINGS, (40, 50, 60, 70))
    assert list(matrix["speed_limit"]) == [40, 50, 60, 70]
    assert len(matrix) == 4


def test_training_and_live_paths_give_identical_rows():
    table = hourly_table(1, limit=60.0, lux=0.1)
    table["water_um"] = 2000.0
    table["temperature_c"] = -3.0
    readings = {
        "illuminance_lux": 0.1, "water_um": 2000.0, "temperature_c": -3.0,
        "wind_strength_kmh": 10.0, "humidity_pct": 80.0, "traffic_cars_s": 15.0,
    }
    training_row = features.training_matrix(table).iloc[0]
    live_row = features.live_matrix(readings, (60,)).iloc[0]
    assert training_row.to_dict() == pytest.approx(live_row.to_dict())


def test_flags_use_router_rules():
    table = hourly_table(1, lux=0.499)
    assert features.training_matrix(table)["is_dark"].iloc[0] == 1
    assert features.training_matrix(hourly_table(1, lux=0.5))["is_dark"].iloc[0] == 0


def test_dark_or_ice_mask():
    table = hourly_table(1, lux=1000.0)
    table.loc[0, "lux"] = 0.1
    table.loc[1, ["water_um", "temperature_c"]] = [2000.0, -1.0]
    mask = features.dark_or_ice_mask(table)
    assert mask.sum() == 2
    assert bool(mask.iloc[0]) and bool(mask.iloc[1])
