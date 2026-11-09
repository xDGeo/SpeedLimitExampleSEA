import math

import pytest

from core import weather_policy as wp

SUPPORT = {40: 7, 50: 55, 60: 230, 70: 97}


def preds(values):
    return [wp.CandidatePrediction(limit, mean, mean * 0.9, mean * 1.1, 0.5)
            for limit, mean in zip((40, 50, 60, 70), values)]


def choose(values):
    return wp.choose_limit(preds(values), skill_pct=-2.0, support_hours=SUPPORT, inside_training_range=True)


def test_highest_limit_meeting_target():
    decision = choose([0.5, 0.7, 0.9, 1.2])
    assert decision.limit_kmh == 60
    assert decision.reduction_kmh == 20
    assert decision.req1_met


def test_exactly_one_meets_target():
    decision = choose([0.5, 0.7, 0.9, 1.0])
    assert decision.limit_kmh == 70
    assert decision.req1_met


def test_none_meets_target_picks_lowest_prediction():
    decision = choose([1.9, 1.4, 1.3, 1.1])
    assert decision.limit_kmh == 70
    assert not decision.req1_met
    assert "REQ1 not met" in decision.reason


def test_lowest_prediction_may_be_in_the_middle():
    assert choose([1.9, 1.2, 1.5, 1.6]).limit_kmh == 50


def test_tie_takes_slower_limit():
    assert choose([1.5, 1.2, 1.2, 1.6]).limit_kmh == 50


def test_guardrail_rejects_unknown_limit():
    bad = preds([1, 1, 1]) + [wp.CandidatePrediction(65, 1.0, 0.9, 1.1, 0.5)]
    with pytest.raises(wp.InvalidPrediction):
        wp.choose_limit(bad, -2.0, SUPPORT, True)


@pytest.mark.parametrize("value", [math.nan, math.inf, -0.5])
def test_guardrail_rejects_impossible_prediction(value):
    with pytest.raises(wp.InvalidPrediction):
        choose([value, 1.0, 1.0, 1.0])


def test_guardrail_rejects_empty():
    with pytest.raises(wp.InvalidPrediction):
        wp.choose_limit([], -2.0, SUPPORT, True)


def test_confidence_attached_for_chosen_limit():
    decision = choose([1.2, 1.4, 1.3, 0.9])
    assert decision.confidence.level == "Low"
    assert decision.confidence.reasons


def test_predictions_kept_for_display():
    assert [p.limit_kmh for p in choose([1, 1, 1, 1]).predictions] == [40, 50, 60, 70]
