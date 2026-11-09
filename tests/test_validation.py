import numpy as np
import pandas as pd
import pytest

import train
from core import validation
from tests.helpers import hourly_table


def failed_names(result):
    return {check.name for check in result.checks if not check.passed and check.severity == "hard"}


def test_clean_table_passes():
    result = validation.validate(hourly_table(), source_near_total=744)
    assert result.passed
    assert not failed_names(result)


def test_missing_hour_fails():
    result = validation.validate(hourly_table().iloc[1:])
    assert "complete_hours" in failed_names(result)


def test_duplicate_hour_fails():
    table = hourly_table()
    table.loc[1, ["day", "hour"]] = table.loc[0, ["day", "hour"]].values
    assert "unique_hours" in failed_names(validation.validate(table))


def test_missing_feature_value_fails():
    table = hourly_table()
    table.loc[3, "temperature_c"] = np.nan
    assert "no_missing_values" in failed_names(validation.validate(table))


def test_value_out_of_range_fails():
    table = hourly_table()
    table.loc[3, "temperature_c"] = 500.0
    assert "values_in_range" in failed_names(validation.validate(table))


def test_illegal_speed_limit_fails():
    table = hourly_table()
    table.loc[3, "speed_limit"] = 65.0
    assert "legal_speed_limits" in failed_names(validation.validate(table))


def test_licence_plate_column_fails():
    table = hourly_table()
    table["LicencePlate"] = "AB 123"
    assert "no_personal_data" in failed_names(validation.validate(table))


def test_label_total_must_reconcile():
    result = validation.validate(hourly_table(), source_near_total=10)
    assert "labels_reconcile" in failed_names(result)


def test_redundant_sensors_must_agree():
    wide = pd.DataFrame({
        15: np.arange(744.0), 18: np.arange(744.0), 19: np.random.default_rng(0).normal(size=744),
    })
    result = validation.validate(hourly_table(), sensor_wide=wide)
    assert "redundant_sensors_agree" in failed_names(result)


def test_low_support_is_only_a_warning():
    table = hourly_table()
    table.loc[0, "speed_limit"] = 40.0
    result = validation.validate(table)
    assert result.passed
    assert any(c.name == "support_per_limit" and not c.passed and c.severity == "warning"
               for c in result.checks)


def test_raise_if_failed():
    with pytest.raises(validation.DataValidationError):
        validation.validate(hourly_table().iloc[1:]).raise_if_failed()


def test_result_is_serialisable():
    payload = validation.validate(hourly_table()).to_dict()
    assert payload["passed"] is True
    assert payload["checks"][0].keys() >= {"name", "passed", "severity", "detail"}


def test_train_refuses_failing_data(tmp_path):
    broken = hourly_table().iloc[1:]
    with pytest.raises(validation.DataValidationError):
        train.run(table=broken, artifacts_dir=tmp_path)
    assert not (tmp_path / "model.pt").exists()
