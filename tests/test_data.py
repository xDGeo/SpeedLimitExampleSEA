import numpy as np
import pandas as pd
import pytest

from core import config, data
from tests.helpers import raw_rows, write_readings


def clean(rows):
    long, report = data.clean_readings(rows)
    return long, report


def test_load_with_header_and_bom(tmp_path):
    frame = data.load_readings(write_readings(tmp_path / "a.csv", raw_rows(1)))
    assert list(frame.columns)[:2] == ["Month", "Day"]
    assert len(frame) == 24 * 17
    assert frame.iloc[0]["Month"] == "1"


def test_load_without_header(tmp_path):
    frame = data.load_readings(write_readings(tmp_path / "a.csv", raw_rows(1), header=False))
    assert len(frame) == 24 * 17
    assert frame.iloc[0]["Sensor"] == "1"


def test_load_real_files_have_expected_rows():
    assert len(data.load_readings(config.READINGS_YEAR_N)) == 12648
    assert len(data.load_readings(config.READINGS_YEAR_N1)) == 12648


def test_sensor_types_are_trimmed():
    types = data.load_sensor_types()
    assert "W" in set(types["code"])
    assert "wind direction" in set(types["type"])
    assert "degrees" in set(types["unit"])


def test_sensor_type_T_is_used_twice_in_source():
    types = data.load_sensor_types()
    assert set(types[types["code"] == "T"]["type"]) == {"temperature", "traffic"}


def test_licence_plate_dropped_at_load():
    assert "LicencePlate" not in data.load_accidents(config.ACCIDENTS_YEAR_N).columns


def test_decimal_comma_parsed():
    long, _ = clean(raw_rows(1))
    assert long.query("Sensor == 15")["value"].iloc[0] == pytest.approx(-5.0)


def test_month_name_and_null_repaired():
    rows = raw_rows(1)
    rows.loc[0, "Month"] = "January"
    rows.loc[1, "Month"] = "NULL"
    long, report = clean(rows)
    assert len(long) == len(rows)
    assert report["months_repaired"] == 2


def test_empty_sensor_id_dropped_and_counted():
    rows = raw_rows(1)
    rows.loc[0, "Sensor"] = ""
    long, report = clean(rows)
    assert len(long) == len(rows) - 1
    assert report["rows_without_sensor"] == 1


def test_empty_value_dropped_and_counted():
    rows = raw_rows(1)
    rows.loc[0, "Value"] = ""
    _, report = clean(rows)
    assert report["empty_values"] == 1


def test_duplicates_removed():
    rows = raw_rows(1)
    rows = pd.concat([rows, rows.iloc[:5]], ignore_index=True)
    long, report = clean(rows)
    assert report["duplicates_removed"] == 5
    assert len(long) == 24 * 17


def test_out_of_range_value_removed():
    rows = raw_rows(1)
    index = rows.index[rows["Sensor"] == "15"][0]
    rows.loc[index, "Value"] = "500,00"
    _, report = clean(rows)
    assert report["out_of_range"] == 1


def test_invalid_speed_limit_removed():
    rows = raw_rows(1)
    index = rows.index[rows["Sensor"] == "-1"][0]
    rows.loc[index, "Value"] = "65,00"
    _, report = clean(rows)
    assert report["out_of_range"] == 1


def test_unknown_sensor_ignored_and_counted():
    rows = raw_rows(1)
    rows.loc[0, "Sensor"] = "99"
    _, report = clean(rows)
    assert report["unknown_sensor_rows"] == 1


def test_hourly_table_has_every_hour():
    long, _ = clean(raw_rows())
    table, wide, _ = data.hourly_table(long)
    assert len(table) == 744
    assert wide.shape[0] == 744
    assert not table.isna().any().any()


def test_median_ignores_one_faulty_sensor():
    rows = raw_rows(1)
    index = rows.index[(rows["Sensor"] == "15") & (rows["Hour"] == "3")][0]
    rows.loc[index, "Value"] = "60,00"
    long, _ = clean(rows)
    table, _, _ = data.hourly_table(long, days=1)
    assert table.query("hour == 3")["temperature_c"].iloc[0] == pytest.approx(-5.0)


def test_one_sensor_missing_a_whole_day_is_imputed_from_peers():
    rows = raw_rows(3)
    rows = rows[~((rows["Sensor"] == "15") & (rows["Day"] == "2"))]
    long, _ = clean(rows)
    table, _, _ = data.hourly_table(long, days=3)
    assert len(table) == 72
    assert table["temperature_c"].eq(-5.0).all()


def test_missing_hour_is_filled():
    rows = raw_rows(3)
    rows = rows[~((rows["Day"] == "2") & (rows["Hour"] == "5"))]
    long, _ = clean(rows)
    table, _, report = data.hourly_table(long, days=3)
    assert len(table) == 72
    assert not table.isna().any().any()
    assert report["hours_filled"] == 1


def test_speed_limit_filled_forward_not_interpolated():
    rows = raw_rows(1)
    rows.loc[(rows["Sensor"] == "-1") & (rows["Hour"] == "0"), "Value"] = "40,00"
    rows.loc[(rows["Sensor"] == "-1") & (rows["Hour"] == "2"), "Value"] = "60,00"
    rows = rows[~((rows["Sensor"] == "-1") & (rows["Hour"] == "1"))]
    long, _ = clean(rows)
    table, _, _ = data.hourly_table(long, days=1)
    assert table.query("hour == 1")["speed_limit"].iloc[0] == 40.0


def test_real_year_n_builds_cleanly():
    result = data.build_hourly(config.READINGS_YEAR_N)
    assert len(result.table) == 744
    assert not result.table.isna().any().any()
    assert np.isclose(result.table["speed_limit"].mean(), result.wide[-1].mean())
    assert {7, 10, 17} == set(result.report["sensors_without_readings"])
    assert result.report["undocumented_sensors"] == [19]
