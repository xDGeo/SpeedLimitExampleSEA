from core import confidence as c

GOOD = dict(skill_pct=10.0, mean=1.0, low=0.9, high=1.1, support_hours=200, inside_training_range=True)


def test_all_checks_good_is_high():
    assert c.nn_confidence(**GOOD).level == "High"


def test_no_skill_caps_at_low():
    result = c.nn_confidence(**{**GOOD, "skill_pct": -3.0})
    assert result.level == "Low"
    assert any("guessing the average" in reason for reason in result.reasons)


def test_skill_within_noise_counts_as_no_skill():
    result = c.nn_confidence(**{**GOOD, "skill_pct": 0.4})
    assert result.level == "Low"
    assert any("guessing the average" in reason for reason in result.reasons)


def test_small_positive_skill_caps_at_medium():
    assert c.nn_confidence(**{**GOOD, "skill_pct": 2.0}).level == "Medium"


def test_wide_disagreement_lowers_level():
    assert c.nn_confidence(**{**GOOD, "low": 0.5, "high": 1.5}).level == "Low"
    assert c.nn_confidence(**{**GOOD, "low": 0.8, "high": 1.2}).level == "Medium"


def test_low_support_lowers_level():
    result = c.nn_confidence(**{**GOOD, "support_hours": 7})
    assert result.level == "Low"
    assert any("7" in reason for reason in result.reasons)
    assert c.nn_confidence(**{**GOOD, "support_hours": 50}).level == "Medium"


def test_out_of_range_input_is_low():
    assert c.nn_confidence(**{**GOOD, "inside_training_range": False}).level == "Low"


def test_nn_always_gives_one_reason_per_check():
    assert len(c.nn_confidence(**GOOD).reasons) == 4


def test_llm_full_agreement_is_high():
    assert c.llm_confidence([20, 20, 20]).level == "High"


def test_llm_two_of_three_is_medium():
    assert c.llm_confidence([20, 20, 10]).level == "Medium"


def test_llm_no_majority_is_low():
    assert c.llm_confidence([0, 10, 20]).level == "Low"


def test_llm_invalid_answers_lower_level():
    assert c.llm_confidence([20, 20], invalid=1).level == "Medium"
    assert c.llm_confidence([20], invalid=2).level == "Low"


def test_llm_fallback_has_no_confidence():
    result = c.llm_confidence([], fallback=True)
    assert result.level == "No confidence"
    assert any("rule-based" in reason for reason in result.reasons)


def test_llm_reasons_state_consistency_not_correctness():
    assert any("not correctness" in reason for reason in c.llm_confidence([0, 0, 0]).reasons)


def test_rule_is_not_a_prediction():
    assert c.rule_confidence().level == "Rule, not a prediction"


def test_to_dict():
    payload = c.llm_confidence([0, 0, 0]).to_dict()
    assert set(payload) == {"level", "reasons"}
