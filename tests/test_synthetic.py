import json

import numpy as np
import pytest

import synthetic_experiment as se
from core import config, features
from tests.helpers import hourly_table

SHAPES = se.ASSUMPTIONS
FASTER, SLOWER, NO_EFFECT = list(SHAPES)


def real_table(days=12, seed=0):
    rng = np.random.default_rng(seed)
    table = hourly_table(days)
    table["speed_limit"] = rng.choice(config.CANDIDATE_LIMITS, len(table)).astype(float)
    table["y"] = rng.poisson(1.2, len(table)).astype(float)
    table["y_next"] = rng.poisson(1.2, len(table)).astype(float)
    return table


def small_run(tmp_path, real=None):
    return se.run(real=real if real is not None else real_table(), repeats=1, factors=(1,), members=1,
                  replay_members=1, replay_rows=200, factor=2, artifacts_dir=tmp_path, docs_dir=tmp_path)


def test_jittered_keeps_only_dark_or_icy_hours():
    base = real_table()
    base["lux"] = 0.49
    result = se.jittered(base, 500, np.random.default_rng(1))
    assert 0 < len(result) < 500
    assert features.dark_or_ice_mask(result).all()


def test_jittered_stays_in_allowed_ranges():
    base = real_table()
    base["humidity_pct"] = 100.0
    base["traffic_cars_s"] = 0.0
    result = se.jittered(base, 500, np.random.default_rng(1))
    assert result["humidity_pct"].le(100).all()
    assert result["traffic_cars_s"].ge(0).all()


def test_jittered_does_not_change_its_input():
    base = real_table()
    copy = base.copy()
    se.jittered(base, 100, np.random.default_rng(1))
    assert base.equals(copy)


def test_assumed_uses_only_candidate_limits():
    result = se.assumed(real_table(), 500, np.random.default_rng(1), SHAPES[FASTER], 1.2)
    assert set(result["speed_limit"]) <= set(map(float, config.CANDIDATE_LIMITS))


@pytest.mark.parametrize("name, faster_is_higher", [(FASTER, True), (SLOWER, False)])
def test_assumed_rates_follow_the_assumption(name, faster_is_higher):
    result = se.assumed(real_table(), 8000, np.random.default_rng(1), SHAPES[name], 1.2)
    rates = result.groupby("speed_limit")["y"].mean()
    assert bool(rates[70.0] > rates[40.0]) is faster_is_higher


def test_no_effect_assumption_is_flat_at_the_real_rate():
    result = se.assumed(real_table(), 20000, np.random.default_rng(1), SHAPES[NO_EFFECT], 1.2)
    rates = result.groupby("speed_limit")["y"].mean()
    assert rates.max() - rates.min() < 0.1
    assert result["y"].mean() == pytest.approx(1.2, abs=0.05)


def test_folds_never_share_a_day():
    real = real_table()
    for _, train, val, test in se.folds(real, repeats=2):
        assert not set(train) & set(val) | set(train) & set(test) | set(val) & set(test)
        assert set(train) | set(val) | set(test) == set(real["day"])


def test_report_has_both_studies(tmp_path):
    report = small_run(tmp_path)
    assert [row["method"] for row in report["imitation"]][0] == "Real data only"
    assert len(report["imitation"]) == 3
    assert set(report["assumptions"]) == set(SHAPES)
    entry = report["assumptions"][FASTER]
    assert {"skill_synthetic_pct", "skill_real_pct", "predicted_per_hour_by_limit_kmh",
            "limit_kmh_counts", "req1_met_hours", "hours", "confidence_counts"} <= set(entry)
    assert entry["hours"] == len(real_table())


def test_run_is_reproducible(tmp_path):
    first = small_run(tmp_path / "a") if (tmp_path / "a").mkdir() is None else None
    second = small_run(tmp_path / "b") if (tmp_path / "b").mkdir() is None else None
    assert first == second


def test_run_writes_report_doc_and_plots(tmp_path):
    report = small_run(tmp_path)
    assert json.loads((tmp_path / "synthetic_report.json").read_text()) == report
    text = (tmp_path / "SYNTHETIC_DATA.md").read_text(encoding="utf-8")
    assert "near-accidents/h" in text and "km/h" in text and "real held-out days" in text
    assert (tmp_path / "plots" / "09_synthetic_imitation.png").exists()
    assert (tmp_path / "plots" / "10_synthetic_assumptions.png").exists()


def test_run_does_not_replace_the_production_model(tmp_path):
    small_run(tmp_path)
    assert not (tmp_path / "model.pt").exists()
