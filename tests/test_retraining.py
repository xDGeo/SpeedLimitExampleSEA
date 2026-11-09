import numpy as np
import pandas as pd

from core import retraining as r


def wide(seed=0, shift=0.0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({15: rng.normal(shift, 1, 744), 16: rng.normal(15, 2, 744)})


def test_identical_tables_detected():
    assert r.readings_identical(wide(), wide())


def test_different_tables_detected():
    assert not r.readings_identical(wide(0), wide(1))


def test_no_drift_for_identical_inputs():
    result = r.input_drift(wide(), wide())
    assert result["max_ks"] == 0
    assert result["drifted_sensors"] == []


def test_drift_found_when_shifted():
    assert 15 in r.input_drift(wide(), wide(shift=3.0))["drifted_sensors"]


def test_rate_test_significant():
    result = r.rate_test(964, 822)
    assert abs(result["z"] - 3.36) < 0.02
    assert result["p_value"] < 0.01


def test_rate_test_not_significant():
    assert r.rate_test(100, 102)["p_value"] > 0.5


def test_identical_inputs_mean_clarify_data_first():
    decision = r.recommend(identical=True, rate_p=0.001, frozen_skill_pct=-5, retrained_gain_pct=1)
    assert decision["decision"] == "Do not retrain yet: clarify the data"
    assert decision["reasons"]


def test_retrain_when_new_model_clearly_better():
    decision = r.recommend(identical=False, rate_p=0.2, frozen_skill_pct=8, retrained_gain_pct=12)
    assert decision["decision"] == "Retrain"


def test_keep_when_nothing_changed():
    decision = r.recommend(identical=False, rate_p=0.6, frozen_skill_pct=8, retrained_gain_pct=0.5)
    assert decision["decision"] == "No retraining needed"
