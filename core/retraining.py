"""RetrainingAnalysis: compares Year N+1 with the trained model."""
import math

import numpy as np
import pandas as pd
from scipy import stats

from core import config, data, features, labels, model


def readings_identical(first: pd.DataFrame, second: pd.DataFrame) -> bool:
    return first.equals(second)


def input_drift(first: pd.DataFrame, second: pd.DataFrame) -> dict:
    per_sensor = {}
    for sensor in first.columns.intersection(second.columns):
        per_sensor[int(sensor)] = float(stats.ks_2samp(first[sensor].dropna(), second[sensor].dropna()).statistic)
    drifted = [sensor for sensor, ks in per_sensor.items() if ks > config.KS_DRIFT_THRESHOLD]
    return {"per_sensor_ks": per_sensor, "max_ks": max(per_sensor.values(), default=0.0), "drifted_sensors": drifted}


def rate_test(count_first: int, count_second: int) -> dict:
    """Two Poisson counts over the same exposure: z test on the difference."""
    z = (count_first - count_second) / math.sqrt(count_first + count_second)
    return {"count_first": count_first, "count_second": count_second, "z": z,
            "p_value": float(2 * stats.norm.sf(abs(z)))}


def recommend(identical: bool, rate_p: float, frozen_skill_pct: float, retrained_gain_pct: float) -> dict:
    if identical:
        return {
            "decision": "Do not retrain yet: clarify the data",
            "reasons": [
                "Year N+1 sensor readings are identical to Year N, which is not plausible for a real year",
                f"Near-accidents changed (p = {rate_p:.4f}) while the inputs did not",
                "Retraining on a possibly wrong file would only adjust the base rate",
            ],
        }
    if retrained_gain_pct >= config.RETRAIN_GAIN_PCT:
        return {"decision": "Retrain", "reasons": [f"A retrained model is {retrained_gain_pct:.1f} points better"]}
    return {"decision": "No retraining needed",
            "reasons": [f"A retrained model is only {retrained_gain_pct:.1f} points better"]}


def analyse(ensemble, n_members=3, folds=5, repeats=2) -> dict:
    year_n = data.build_hourly(config.READINGS_YEAR_N)
    year_n1 = data.build_hourly(config.READINGS_YEAR_N1)
    accidents_n = data.load_accidents(config.ACCIDENTS_YEAR_N)
    accidents_n1 = data.load_accidents(config.ACCIDENTS_YEAR_N1)

    identical = readings_identical(year_n.wide, year_n1.wide)
    drift = input_drift(year_n.wide, year_n1.wide)
    near_n = labels.label_report(accidents_n)["near_accidents"]
    near_n1 = labels.label_report(accidents_n1)["near_accidents"]
    rate = rate_test(near_n, near_n1)

    table = labels.attach_labels(year_n1.table, accidents_n1)
    risky = table[features.dark_or_ice_mask(table)].reset_index(drop=True)
    X, y = features.training_matrix(risky), risky["near_accidents"].to_numpy(dtype=float)
    frozen_mu = ensemble.predict(X)

    train_table = labels.attach_labels(year_n.table, accidents_n)
    train_risky = train_table[features.dark_or_ice_mask(train_table)]
    constant = float(train_risky["near_accidents"].mean())

    frozen = model.evaluate(y, frozen_mu)
    baseline = model.evaluate(y, np.full(len(y), constant))
    frozen_skill = model.skill_pct(frozen["poisson_deviance"], baseline["poisson_deviance"])
    retrained = model.cross_validated_skill(X, y, risky["day"], n_members=n_members, folds=folds, repeats=repeats)
    gain = retrained["skill_pct"] - frozen_skill
    return {
        "inputs_identical": identical,
        "input_drift": drift,
        "near_accident_rate": rate,
        "dark_or_ice_rate_per_hour": {"year_n": constant, "year_n_plus_1": float(y.mean())},
        "frozen_model_on_year_n_plus_1": frozen,
        "year_n_mean_as_constant_on_year_n_plus_1": baseline,
        "frozen_skill_pct": frozen_skill,
        "retrained_cv": retrained,
        "retrained_gain_points": gain,
        "recommendation": recommend(identical, rate["p_value"], frozen_skill, gain),
    }
