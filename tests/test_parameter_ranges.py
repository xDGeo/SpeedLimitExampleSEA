import math

import pytest

from core import parameter_ranges as pr
from tests.helpers import DAY_READINGS

BANDS = {"wind_strength_kmh": (0.0, 40.0), "humidity_pct": (50.0, 95.0), "traffic_cars_s": (4.0, 25.0)}


def test_every_parameter_has_a_unit():
    expected = {"illuminance_lux": "lux", "water_um": "µm", "temperature_c": "°C",
                "wind_strength_kmh": "km/h", "humidity_pct": "%", "traffic_cars_s": "cars/s",
                "pm10": "µg/m³", "no2": "µg/m³"}
    assert {key: param.unit for key, param in pr.PARAMETERS.items()} == expected


@pytest.mark.parametrize("lux, status", [(0.499, "Abnormal"), (0.5, "Normal"), (50000, "Normal")])
def test_illuminance_boundary(lux, status):
    assert pr.classify("illuminance_lux", lux).status == status


@pytest.mark.parametrize("water, temp, status", [
    (1000, -1, "Normal"), (1001, -1, "Abnormal"), (1001, 0, "Normal"), (5000, 5, "Normal"),
])
def test_water_needs_temperature_context(water, temp, status):
    assert pr.classify("water_um", water, context={"temperature_c": temp}).status == status


@pytest.mark.parametrize("temp, water, status", [(-1, 1001, "Abnormal"), (-1, 1000, "Normal"), (0, 1001, "Normal")])
def test_temperature_needs_water_context(temp, water, status):
    assert pr.classify("temperature_c", temp, context={"water_um": water}).status == status


@pytest.mark.parametrize("key, value, status", [
    ("pm10", 50, "Normal"), ("pm10", 51, "Abnormal"), ("no2", 200, "Normal"), ("no2", 201, "Abnormal"),
])
def test_air_quality_limits(key, value, status):
    assert pr.classify(key, value).status == status


def test_data_derived_band_is_informational():
    result = pr.classify("wind_strength_kmh", 90, bands=BANDS)
    assert result.status == "Abnormal"
    assert "does not change the limit" in result.reason


def test_no_band_means_unknown():
    assert pr.classify("humidity_pct", 70, bands={}).status == "Unknown"


def test_every_classification_has_a_reason():
    for key in pr.PARAMETERS:
        result = pr.classify(key, 1.0, context={"temperature_c": 5, "water_um": 0}, bands=BANDS)
        assert result.reason


def test_valid_readings_pass():
    pr.validate_readings(DAY_READINGS)


@pytest.mark.parametrize("key, value", [
    ("temperature_c", 71), ("temperature_c", -31), ("humidity_pct", -1), ("humidity_pct", 101),
    ("illuminance_lux", -0.1), ("water_um", 10001), ("traffic_cars_s", 51),
    ("wind_strength_kmh", 301), ("temperature_c", math.nan), ("temperature_c", math.inf),
    ("temperature_c", "cold"),
])
def test_invalid_readings_rejected(key, value):
    with pytest.raises(pr.InvalidReading):
        pr.validate_readings({**DAY_READINGS, key: value})


def test_missing_reading_rejected():
    readings = dict(DAY_READINGS)
    del readings["water_um"]
    with pytest.raises(pr.InvalidReading):
        pr.validate_readings(readings)


def test_format_value_includes_unit():
    assert pr.format_value("wind_strength_kmh", 12.34) == "12.3 km/h"
    assert pr.format_value("temperature_c", -1) == "-1.0 °C"


def test_ranges_table_separates_rules_from_data():
    table = pr.ranges_table(BANDS)
    assert set(table["Type"]) == {"Rule: changes the limit", "Data band: informational only"}
    assert {"Parameter", "Unit", "Allowed range", "Normal", "Abnormal", "Basis"} <= set(table.columns)
    assert len(table) == len(pr.PARAMETERS)
