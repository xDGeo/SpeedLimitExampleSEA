import json

import pandas as pd
import pytest

from core import air_quality as aq, confidence, cycle
from core.llm_manager import AirDecision
from tests.helpers import DAY_READINGS, NIGHT_READINGS


class FakePredictor:
    meta = {"skill_pct": -3.0, "support_hours": {40: 7, 50: 55, 60: 230, 70: 97}}

    def __init__(self, means=(1.5, 1.3, 1.2, 1.1), fail=False):
        self.means, self.fail = means, fail

    def summary(self, X):
        if self.fail:
            raise RuntimeError("no model")
        return pd.DataFrame({
            "mean": self.means, "low": [m * 0.9 for m in self.means],
            "high": [m * 1.1 for m in self.means], "p_le_target": [0.1] * 4,
        })

    def in_training_range(self, X):
        return pd.Series([True] * len(X)).values


class FakeLLM:
    def __init__(self, reduction=0, source="llm", review=False):
        self.reduction, self.source, self.review = reduction, source, review
        self.calls = 0

    def decide(self, pm10, no2):
        self.calls += 1
        return AirDecision(
            reduction_kmh=self.reduction, limit_kmh=80 - self.reduction,
            confidence=confidence.llm_confidence([self.reduction] * 3), answers=[self.reduction] * 3,
            reason="air reason", source=self.source, review=self.review,
        )


class FakeAir:
    def __init__(self, fail=False):
        self.fail = fail

    def get_forecast(self):
        if self.fail:
            raise aq.AirQualityUnavailable("down")
        return aq.AirQuality(10.0, 20.0, "Open-Meteo forecast")


def build(tmp_path, predictor=None, llm=None, air=None):
    return cycle.SpeedLimitCycle(
        predictor=predictor or FakePredictor(), llm=llm or FakeLLM(), air_client=air or FakeAir(),
        log_path=tmp_path / "decisions.jsonl",
    )


def log_lines(tmp_path):
    return [json.loads(line) for line in (tmp_path / "decisions.jsonl").read_text().splitlines()]


def test_clear_day_good_air_is_80(tmp_path):
    result = build(tmp_path).run(DAY_READINGS)
    assert result.status == "published"
    assert result.limit_kmh == 80
    assert result.reduction_kmh == 0
    assert result.weather is None


def test_dark_uses_network(tmp_path):
    result = build(tmp_path).run(NIGHT_READINGS)
    assert result.route.use_nn
    assert result.limit_kmh == 70
    assert not result.req1_met
    assert result.weather.confidence.level == "Low"


def test_daylight_black_ice_uses_network(tmp_path):
    result = build(tmp_path).run({**DAY_READINGS, "water_um": 1001, "temperature_c": -1})
    assert result.route.black_ice and result.weather is not None


def test_poor_air_reduces_limit(tmp_path):
    result = build(tmp_path, llm=FakeLLM(30)).run(DAY_READINGS)
    assert result.limit_kmh == 50
    assert result.air.confidence.level == "High"


def test_dark_and_poor_air_take_strictest(tmp_path):
    assert build(tmp_path, llm=FakeLLM(30)).run(NIGHT_READINGS).limit_kmh == 50


def test_air_override_is_used(tmp_path):
    air = FakeAir(fail=True)
    result = build(tmp_path, air=air).run(DAY_READINGS, air_override=aq.manual_reading(60, 210))
    assert result.air_reading.source == "Manual override"
    assert not result.review


def test_air_api_down_flags_review_without_reduction(tmp_path):
    result = build(tmp_path, air=FakeAir(fail=True)).run(DAY_READINGS)
    assert result.limit_kmh == 80
    assert result.review
    assert any("Air quality" in reason for reason in result.reasons)


def test_invalid_input_rejected_and_limit_kept(tmp_path):
    system = build(tmp_path)
    assert system.run(NIGHT_READINGS).limit_kmh == 70
    rejected = system.run({**DAY_READINGS, "temperature_c": 500})
    assert rejected.status == "rejected"
    assert rejected.limit_kmh == 70
    assert system.last_limit == 70


def test_invalid_first_input_publishes_nothing(tmp_path):
    rejected = build(tmp_path).run({**DAY_READINGS, "humidity_pct": -1})
    assert rejected.status == "rejected"
    assert rejected.limit_kmh is None


def test_network_failure_uses_fixed_limit_and_review(tmp_path):
    result = build(tmp_path, predictor=FakePredictor(fail=True)).run(NIGHT_READINGS)
    assert result.limit_kmh == 60
    assert result.review


def test_llm_fallback_flags_review(tmp_path):
    result = build(tmp_path, llm=FakeLLM(0, source="rule-based fallback", review=True)).run(DAY_READINGS)
    assert result.review


def test_audit_record_written(tmp_path):
    build(tmp_path).run(NIGHT_READINGS, source="scheduler")
    record = log_lines(tmp_path)[0]
    assert record["source"] == "scheduler"
    assert record["limit_kmh"] == 70
    assert record["unit"] == "km/h"
    assert record["predictions"][0]["limit_kmh"] == 40
    assert record["nn_confidence"]["level"] == "Low"
    assert record["llm_confidence"]["level"] == "High"
    assert record["req1_met"] is False


def test_rejected_input_logged(tmp_path):
    build(tmp_path).run({**DAY_READINGS, "humidity_pct": -1})
    assert log_lines(tmp_path)[0]["status"] == "rejected"


def test_override_published_and_logged(tmp_path):
    system = build(tmp_path)
    system.run(NIGHT_READINGS)
    assert system.apply_override(50, "fog reported").limit_kmh == 50
    assert system.last_limit == 50
    assert log_lines(tmp_path)[-1]["source"] == "operator"


def test_override_must_be_legal(tmp_path):
    with pytest.raises(ValueError):
        build(tmp_path).apply_override(55)
